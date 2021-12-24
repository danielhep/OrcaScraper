import datetime
from pendulum import tz
import scrapy
import logging
from scrapy.loader import ItemLoader
import pendulum
from OrcaScraper.items import TransactionItem


def authentication_failed(response):
    if response.url == "https://orcacard.com/ERG-Seattle/welcomePage.do":
        return False
    else:
        return True


class OrcaSpider(scrapy.Spider):
    name = "orca"
    allowed_domains = ["orcacard.com"]
    start_urls = ["https://orcacard.com/ERG-Seattle/p1_001.do/"]

    def __init__(
        self,
        username=None,
        password=None,
        startdate=None,
        enddate=None,
        year=pendulum.today(tz='America/Los_Angeles').year,
        *args,
        **kwargs
    ):
        super(OrcaSpider, self).__init__(*args, **kwargs)
        if username == None or password == None:
            raise Exception("No username or password provided.")

        if startdate == None:
            self.startdate = pendulum.datetime(year, 1, 1, tz='America/Los_Angeles')
        else:
            self.startdate = pendulum.parse(startdate, strict=False)
        if enddate == None:
            if year == pendulum.today(tz='America/Los_Angeles').year:
                # Use today's date so we don't generate a date in the future
                self.enddate = pendulum.today(tz='America/Los_Angeles')
            else:
                # Otherwise use last day of the year
                self.enddate = pendulum.datetime(year, 12, 31, tz="America/Los_Angeles")
        else:
            self.enddate = pendulum.parse(enddate, strict=False)

        self.username = username
        self.password = password

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={"j_username": self.username, "j_password": self.password},
            callback=self.after_login,
        )

    def after_login(self, response):
        if authentication_failed(response):
            self.logger.error("Login failed")
            return
        else:
            self.logger.debug("Login succeeded")
            activityPage = response.xpath(
                "//a[contains(.,'View all activity')]/@href"
            ).get()
            yield response.follow(activityPage, callback=self.parse_activity)

    def parse_activity(self, response):
        for option in response.css("#card-details option"):
            # Process each ORCA card on the account
            logging.debug(self.startdate.month)
            yield scrapy.FormRequest.from_response(
                response,
                formdata={
                    "searchStartMonth": str(self.startdate.month),
                    "searchStartDay": str(self.startdate.day),
                    "searchStartYear": str(self.startdate.year),
                    "searchEndMonth": str(self.enddate.month),
                    "searchEndDay": str(self.enddate.day),
                    "searchEndYear": str(self.enddate.year),
                    "selectedCardSerialNumber": option.xpath("@value").get(),
                },
                callback=self.parse_card_data,
            )

    def parse_card_data(self, response):
        cardSN = (
            response.xpath("//tr[contains(.,'Card Serial Number:')]/td/text()")
            .get()
            .strip()
        )
        results = response.css("#resultTable tbody tr")
        for result in results:
            il = ItemLoader(TransactionItem(), result)
            il.add_value("sn", cardSN)
            il.add_xpath("date", "td[1]/text()")
            il.add_xpath("desc", "td[2]/text()")
            il.add_xpath("location", "td[3]/text()")
            il.add_xpath("product", "td[4]/text()")
            il.add_xpath("amount", "td[5]/text()")
            il.add_xpath("balance", "td[6]/text()")
            il.add_xpath("paymentMethod", "td[7]/text()")
            yield il.load_item()
        nextButtonHref = response.xpath("//a[contains(.,'Next')]/@href").get()
        if bool(nextButtonHref):
            logging.debug("Next page.")
            yield response.follow(nextButtonHref, callback=self.parse_card_data)
