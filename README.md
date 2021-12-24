# OrcaScraper
This project allows you to scrape the data from your ORCA cards on https://orcacard.com/ into a JSON file. 

By default it grabs all transactions for a given year, but it's possible to give it any start and stop date. 
It will grab transactions for every ORCA card in your account, collecting all into the same array, but with the card's serial number stored with each transaction.
The data will likely need to be cleaned up and filtered in a separate program to make it useful.

## How To Run
Ensure you have Python, pip, and pipenv installed on your computer. Then, inside the project, install dependencies with:

```shell
pipenv install
```

Then, run the project:
```shell
# Grab all transactions for current calendar year.
pipenv run scrapy crawl orca -o out.json -a username=yourusername -a password=yourpass
# Grab all transactions for a given calendar year.
pipenv run scrapy crawl orca -o out.json -a username=yourusername -a password=yourpass -a year=2019
# Grab all transactions for a given date range
pipenv run scrapy crawl orca -o out.json -a username=yourusername -a password=yourpass -a startdate="Mar 1 2020" -a enddate="Aug 29 2020"
```

Set `yourusername` and `yourpass` to your orcacard.com username and password. 
You may omit `pipenv run` by first running `pipenv shell` before your commands. 

Output file can be changed by adjusting `out.json`. Supported file times are `csv`, `json`, and `xml`.
