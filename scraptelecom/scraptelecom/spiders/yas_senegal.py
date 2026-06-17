import scrapy
import re
from datetime import datetime


class YasSenegalSpider(scrapy.Spider):
    name = "yas_senegal"
    allowed_domains = ["yas.sn"]

    start_urls = [
        "https://www.yas.sn/particulier/mobile-plans/internet/",
        "https://www.yas.sn/particulier/home-plans/",
    ]

    ROUTE_MAP = {
        "/particulier/mobile-plans/internet/": "parse_mobile_internet",
        "/particulier/home-plans/": "parse_home_plans",
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

    # =========================
    # MOBILE INTERNET
    # =========================

    def parse_mobile_internet(self, response):

        cards = response.css("div.eael-tabs-content div.card")

        for card in cards:

            offer_name = card.css(
                "h3.card-btn::text"
            ).get(default="").strip()

            price_raw = card.css(
                "h4.card-price::text"
            ).get(default="").strip()

            features = [
                t.strip()
                for t in card.css("ul li::text").getall()
                if t.strip()
            ]

            volume_match = re.search(
                r'(\d+(?:[.,]\d+)?)\s*(Mo|Go)',
                offer_name,
                re.I
            )

            volume_gb = None

            if volume_match:
                value = float(
                    volume_match.group(1).replace(",", ".")
                )

                unit = volume_match.group(2).lower()

                if unit == "mo":
                    volume_gb = value / 1000
                else:
                    volume_gb = value

            validity_match = re.search(
                r'(\d+)\s*(jours?|h)',
                " ".join(features),
                re.I
            )

            validity_days = None

            if validity_match:

                value = int(validity_match.group(1))
                unit = validity_match.group(2).lower()

                if unit == "h":
                    validity_days = 1
                else:
                    validity_days = value

            yield {

                "operator": "YAS Senegal",
                "country": "Senegal",
                "currency": "XOF",
                "offer_type": "mobile",
                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),

                "offer_name": offer_name,

                "price_local": float(
                    re.sub(r"[^\d]", "", price_raw)
                ) if price_raw else None,

                "data_volume_gb": volume_gb,
                "speed_mbps": None,

                "validity_days": validity_days,

                "install_fee_kmf": None,
                "equipment_fee_kmf": None,

                "calls_fixed": None,
                "calls_mobile_mn": None,

                "is_unlimited": False,

                "media_type": "mobile_data",
                "ls_subtype": None,
            }

    # =========================
    # HOME PLANS / FIBRE
    # =========================

    def parse_home_plans(self, response):

        cards = response.css("div.eael-tabs-content div.card")

        for card in cards:

            offer_name = card.css(
                "h3.card-btn::text"
            ).get(default="").strip()

            price_raw = card.css(
                "h4.card-price::text"
            ).get(default="").strip()

            features = [
                t.strip()
                for t in card.css("ul li::text").getall()
                if t.strip()
            ]

            speed_match = re.search(
                r'(\d+)\s*Mbps',
                offer_name,
                re.I
            )

            speed_mbps = (
                int(speed_match.group(1))
                if speed_match
                else None
            )

            install_match = re.search(
                r'(\d[\d\s]*)\s*FCFA',
                " ".join(features),
                re.I
            )

            install_fee = None

            if install_match:
                install_fee = float(
                    re.sub(
                        r"[^\d]",
                        "",
                        install_match.group(1)
                    )
                )

            calls_match = re.search(
                r'(\d+)\s*min',
                " ".join(features),
                re.I
            )

            calls_mobile = (
                int(calls_match.group(1))
                if calls_match
                else None
            )

            is_unlimited = any(
                "illimité" in f.lower()
                for f in features
            )

            offer_type = (
                "fiber_pro"
                if "pro" in offer_name.lower()
                else "fiber"
            )

            yield {

                "operator": "YAS Senegal",
                "country": "Senegal",
                "currency": "XOF",

                "offer_type": offer_type,

                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),

                "offer_name": offer_name,

                "price_local": float(
                    re.sub(r"[^\d]", "", price_raw)
                ) if price_raw else None,

                "data_volume_gb": None,

                "speed_mbps": speed_mbps,

                "validity_days": 30,

                "install_fee_kmf": install_fee,
                "equipment_fee_kmf": None,

                "calls_fixed": None,
                "calls_mobile_mn": calls_mobile,

                "is_unlimited": is_unlimited,

                "media_type": "fiber",
                "ls_subtype": "ftth",
            }