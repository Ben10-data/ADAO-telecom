import scrapy
import re 
from datetime import datetime


class MytMauritiusSpider(scrapy.Spider):
    name = "myt_mauritius"
    allowed_domains = ["myt.mu"]

    start_urls = [
        "https://www.myt.mu/mobile/prepaid-mobile-data",
        "https://www.myt.mu/mobile/myt-everywhere/",
        "https://www.myt.mu/home/internet-and-tv/broadbandonly",
    ]   

    ROUTE_MAP = {
        "/mobile/prepaid-mobile-data": "parse_mobile_data",
        "/mobile/myt-everywhere/": "parse_everywhere",
        "/home/internet-and-tv/broadbandonly": "parse_fibre_offers",
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

    # Mobile Data Combo Packs
    def parse_mobile_data(self, response):

        cards = response.css(
            "section#prepaid-offers div.container div.col-lg-4"
        )

        for card in cards:

            offer_name = (
                card.css("h2::text")
                .get(default="")
                .strip()
            )

            price_text = (
                card.css("h3.g-font-size-40.g-color-white::text")
                .get(default="")
                .strip()
            )

            price_local = (
                float(re.sub(r"[^\d]", "", price_text))
                if price_text
                else None
            )

            data_text = "".join(
                card.css(
                    "h3.g-font-size-24 *::text, h3.g-font-size-24::text"
                ).getall()
            ).strip()

            validity_text = (
                card.css("h5::text")
                .get(default="")
                .strip()
            )

            # Volume
            data_volume_gb = None
            is_unlimited = False

            if "unlimited" in data_text.lower():
                is_unlimited = True
            else:
                m = re.search(r"(\d+(?:\.\d+)?)\s*(GB|TB)", data_text, re.I)

                if m:
                    value = float(m.group(1))

                    if m.group(2).upper() == "TB":
                        value *= 1024

                    data_volume_gb = value

            # Validité
            validity_days = None

            if "1 hour" in validity_text.lower():
                validity_days = 1

            else:
                m = re.search(r"(\d+)", validity_text)

                if m:
                    validity_days = int(m.group(1))

            sms_code = (
                "".join(
                    card.css(
                        "h3.g-font-size-20 span.g-color-yellow::text"
                    ).getall()[:1]
                )
                .strip()
            )

            yield {
                "operator": "MY.T Mauritius",
                "country": "Mauritius",
                "currency": "Rs",

                "offer_type": "mobile",

                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),

                "offer_name": offer_name,

                "price_local": price_local,

                "data_volume_gb": data_volume_gb,

                "speed_mbps": None,

                "validity_days": validity_days,

                "install_fee": None,
                "equipment_fee": None,

                "calls_fixed": None,
                "calls_mobile_mn": None,

                "is_unlimited": is_unlimited,

                "media_type": "mobile",

                "ls_subtype": sms_code or None,
            }

    # Mobile C-Box
    def parse_everywhere(self, response):

            table = response.css("table")[1]

            offers = [
                x.strip()
                for x in table.css("thead th h2::text").getall()
            ]

            prices = [
                float(re.sub(r"\D", "", x))
                for x in table.css(
                    "tbody tr.g-font-weight-700 td::text"
                ).getall()[1:]
            ]

            speeds_after_cap = [
                x.strip()
                for x in table.xpath(
                    './/tr[td[contains(text(),"Download speed after consumption")]]/td[position()>1]/text()'
                ).getall()
            ]

            for offer_name, price, speed_after_cap in zip(
                offers,
                prices,
                speeds_after_cap
            ):

                # Conversion volume
                data_volume_gb = None

                if "TB" in offer_name:
                    data_volume_gb = (
                        float(
                            re.search(r"(\d+)", offer_name).group(1)
                        ) * 1000
                    )
                else:
                    m = re.search(r"(\d+)", offer_name)
                    if m:
                        data_volume_gb = float(m.group(1))

                speed_mbps = None
                m = re.search(r"(\d+)", speed_after_cap)
                if m:
                    speed_mbps = float(m.group(1))

                yield {
                    "operator": "my.t",
                    "country": "Mauritius",
                    "currency": "Rs",
                    "offer_type": "fixed_wireless",
                    "source_url": response.url,
                    "scraped_at": datetime.utcnow().isoformat(),

                    "offer_name": f"C-Box {offer_name}",
                    "price_local": price,

                    "data_volume_gb": data_volume_gb,
                    "speed_mbps": None,

                    "validity_days": 30,

                    "install_fee": None,
                    "equipment_fee": None,

                    "calls_fixed": None,
                    "calls_mobile_mn": None,

                    "is_unlimited": False,

                    "media_type": "4G/5G",
                    "ls_subtype": "cbox",
                }
 



    def parse_fibre_offers(self, response):

        offers = response.css("section#otherbroadbandonlyoffers section[id]")

        for offer in offers:

            offer_name = offer.css("h2::text").get(default="").strip()

            # Download
            speed_text = " ".join(
                offer.css("div.media-body span::text").getall()
            )
            speed_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:Mbps|Gbps)", speed_text, re.I)

            speed_mbps = speed_match.group(1) if speed_match else None


            # Volume
            volume_text = offer.xpath(
                './/span[contains(text(),"Volume Allowance")]/following::span[1]/text()'
            ).get(default="")

            data_volume_gb = None

            volume_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(GB|TB)",
                volume_text,
                re.I,
            )

            if volume_match:
                value = float(volume_match.group(1))
                unit = volume_match.group(2).upper()

                data_volume_gb = value * 1000 if unit == "TB" else value

            # Prix
            price_text = "".join(
                offer.css("strong span::text").getall()
            )

            price_match = re.search(r"([\d,]+)", price_text)

            price_local = None
            if price_match:
                price_local = float(
                    price_match.group(1).replace(",", "")
                )

            yield {
                "operator": "MY.T Mauritius",
                "country": "Mauritius",
                "currency": "Rs",

                "offer_type": "fibre",

                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),

                "offer_name": offer_name,

                "price_local": price_local,

                "data_volume_gb": data_volume_gb,

                "speed_mbps": float(speed_mbps) if speed_mbps else None,

                "validity_days": 30,

                "install_fee": None,
                "equipment_fee": None,

                "calls_fixed": None,
                "calls_mobile_mn": None,

                "is_unlimited": False,

                "media_type": "fibre",

                "ls_subtype": None,
            }