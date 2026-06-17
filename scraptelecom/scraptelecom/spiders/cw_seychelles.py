import scrapy


class CwSeychellesSpider(scrapy.Spider):
    name = "cw_seychelles"
    allowed_domains = ["cwseychelles.com"]
    start_urls = [
    "https://www.cwseychelles.com/broadband/giga-boosters",
    "https://www.cwseychelles.com/eshop/mobile-internet",
    "https://www.cwseychelles.com/broadband-pro",
    "https://www.cwseychelles.com/wireless-broadband",
    "https://www.cwseychelles.com/giganet",
]

    ROUTE_MAP = {
    "/broadband/giga-boosters": "parse_giga_boosters",
    "/eshop/mobile-internet": "parse_mobile_internet",
    "/broadband-pro": "parse_broadband_pro",
    "/wireless-broadband": "parse_wireless_broadband",
    "/giganet": "parse_giganet",
}

    def parse(self, response):
        method_name = next(
            (v for k, v in self.ROUTE_MAP.items() if k in response.url),
            None
        )

        if method_name:
            yield from getattr(self, method_name)(response)
        else:
            self.logger.warning(f"URL non routée : {response.url}")

    def parse_giga_boosters(self, response):
        pass

    def parse_mobile_internet(self, response):
        pass

    def parse_broadband_pro(self, response):
        pass

    def parse_wireless_broadband(self, response):
        pass

    def parse_giganet(self, response):
        pass