import scrapy


class YasTogoSpider(scrapy.Spider):
    name = "yas_togo"
    allowed_domains = ["yas.tg"]
    start_urls = [
    "https://yas.tg/particulier/forfaits-mobile/internet/",
    "https://yas.tg/particulier/internet-residentiel/fibre-residentielle/",
    "https://yas.tg/particulier/internet-residentiel/5g-home-plan/",
]
    ROUTE_MAP = {
        "/particulier/forfaits-mobile/internet/": "parse_mobile_internet",
        "/particulier/internet-residentiel/fibre-residentielle/": "parse_fibre_residentielle",
        "/particulier/internet-residentiel/5g-home-plan/": "parse_5g_home_plan",
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

    def parse_mobile_internet(self, response):
        pass

    def parse_fibre_residentielle(self, response):
        pass

    def parse_5g_home_plan(self, response):
        pass