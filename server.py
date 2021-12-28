import json
from urllib.parse import parse_qs

from multiprocessing import Process, Manager, Queue
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from server_scrapy_bridge import OrcaTransactionProcessor

class OrcaUserRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/transactions"):
            self.send_error(404)
            return
        try:
            qs_index = self.path.index("?") + 1
            query_string = self.path[qs_index:]
            query_params = parse_qs(query_string)
            username = query_params.get('username', ' ')[0].strip()
            password = query_params.get('password', ' ')[0].strip()
            if not username or not password:
                self.send_error(400, "Username or password not provided.")
                return
            start = query_params.get('start', ' ')[0].strip()
            end = query_params.get('end', ' ')[0].strip()
            self.process(username, password, start or None, end or None)
        except:
            self.send_error(500)
        
    def process(self, username, password, start, end):
        processor = OrcaTransactionProcessor(user=username, pw=password, start=start, end=end)
        q = Queue()
        p = Process(target=processor.fetch, args=(q,))
        p.start()
        p.join()
        result = q.get()
        items = list(map(lambda k : k._values, result))
        if len(items) == 0: #return an error if no transactions found. TODO: Handle auth and other failures better
            self.send_error(400)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        # it's nice to sort them, but putting in a try/except just in case something goes wrong/data format changes/whatever
        try:
            items.sort(key=lambda a : a['date'])
        except:
            pass
        final_result = {
            "transcations": items,
        }
        item_str = json.dumps(final_result)
        self.wfile.write(item_str.encode(encoding='utf_8'))
    
    def version_string(self) -> str:
        return 'orca-pod-1'

def start_server():
    httpd = ThreadingHTTPServer(('localhost', 5069), OrcaUserRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    manager = Manager()
    running_server = Process(target=start_server)
    running_server.start()
    running_server.join()