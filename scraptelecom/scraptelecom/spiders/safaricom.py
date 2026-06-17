import scrapy


class SafaricomSpider(scrapy.Spider):
    name = "safaricom"
    allowed_domains = [
    "safaricom.co.ke",
    "internet.safaricom.co.ke",
    "business.safaricom.co.ke"
]
    start_urls = [
    "https://internet.safaricom.co.ke/",
    "https://internet.safaricom.co.ke/5g-wireless",
    "https://internet.safaricom.co.ke/4g-wifi-router",
    "https://www.safaricom.co.ke/personal/data/data-tariffs",
    "https://www.business.safaricom.co.ke/products/mobilebulkdata",
    "https://www.business.safaricom.co.ke/products/5g",
]

    ROUTE_MAP = {
    "internet.safaricom.co.ke/": "parse_home_internet",
    "/5g-wireless": "parse_5g_wireless",
    "/4g-wifi-router": "parse_4g_wifi_router",
    "/personal/data/data-tariffs": "parse_data_tariffs",
    "/products/mobilebulkdata": "parse_mobile_bulk_data",
    "/products/5g": "parse_business_5g",
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

    def parse_home_internet(self, response):
        pass

    def parse_5g_wireless(self, response):
        pass

    def parse_4g_wifi_router(self, response):
        pass

    def parse_data_tariffs(self, response):
        pass

    def parse_mobile_bulk_data(self, response):
        pass

    def parse_business_5g(self, response):
        pass