import scrapy


class OrangeSenegalSpider(scrapy.Spider):
    name = "orange_senegal"
    allowed_domains = [
    "orange.sn",
    "eligibilite.orange.sn"
]
    start_urls = [
    "https://www.orange.sn/pass-internet",
    "https://eligibilite.orange.sn/home",
]

    def parse(self, response):
        pass
