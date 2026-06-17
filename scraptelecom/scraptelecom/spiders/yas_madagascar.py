import scrapy
import re
from datetime import datetime


class YasMadagascarSpider(scrapy.Spider):
    name = "yas_madagascar"
    allowed_domains = ["yas.mg"]

    start_urls = [
        "https://www.yas.mg/particulier/forfaits-mobiles/internet/",
        "https://www.yas.mg/particulier/internet-fixe/fibre/",
    ]

    ROUTE_MAP = {
        "/forfaits-mobiles/internet/": "parse_internet",
        "/internet-fixe/fibre/": "parse_fibre",
    }

    def parse(self, response):
        method_name = next(
            (v for k, v in self.ROUTE_MAP.items() if k in response.url),
            None
        )

        if method_name:
            yield from getattr(self, method_name)(response)

    # =========================
    # MOBILE INTERNET
    # =========================

    def parse_internet(self, response):

        cards = response.css("div#net-tab div.card")

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

            volume_text = features[0] if len(features) > 0 else ""

            volume_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(Mo|Go|MB|GB|TB)', volume_text, re.I)
             
            if "mo" in volume_match.group(2).lower():
                volume_match = float(volume_match.group(1)) / 1000
            else: 
                volume_match = float(volume_match.group(1).replace(",", ".")) if volume_match else None 

            validity_match = re.search(
                r"(\d+)\s*jours?",
                " ".join(features),
                re.I
            )

            yield {
                "operator": "YAS Madagascar",
                "country": "Madagascar",
                "currency": "MGA",
                "offer_type": "mobile",
                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),

                "offer_name": offer_name,
                "price_local": float(
                    re.sub(r"[^\d]", "", price_raw)
                ) if price_raw else None,

                "data_volume_gb": volume_match if volume_match else None,
                "speed_mbps": None,

                "validity_days": (
                    int(validity_match.group(1))
                    if validity_match
                    else None
                ),

                "install_fee_kmf": None,
                "equipment_fee_kmf": None,
                "calls_fixed": None,
                "calls_mobile_mn": None,

                "is_unlimited": False,

                "media_type": "mobile_data",
                "ls_subtype": None,
            }

    # =========================
    # FIBRE
    # =========================

    def parse_fibre(self, response):

        cards = response.css("div.plan-card-top-wrapper div.card")

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

            fup_text = next(
                (
                    item
                    for item in features
                    if "FUP" in item.upper()
                ),
                None
            )
            
            if "to" in fup_text.lower():
                fup_text = float(re.sub(r"[^\d,]", "", fup_text.replace(",", "."))) * 1000
            else: 
              fup_text = float(re.sub(r"[^\d,]", "", fup_text.replace(",", ".")))
            
        

            calls_fixed_match = re.search(
                r"(\d+)\s*mn",
                " ".join(features),
                re.I
            )

            install_fee = 0 if any(
                "installation offerts" in f.lower()
                or "installation offerte" in f.lower()
                for f in features
            ) else None

            yield {
                "operator": "YAS Madagascar",
                "country": "Madagascar",
                "currency": "MGA",
                "offer_type": "fiber",
                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),

                "offer_name": offer_name,

                "price_local": float(
                    re.sub(r"[^\d]", "", price_raw)
                ) if price_raw else None,

                "data_volume_gb": fup_text,

                "speed_mbps": None,

                "validity_days": 30,

                "install_fee_kmf": install_fee,
                "equipment_fee_kmf": None,

                "calls_fixed": (
                    int(calls_fixed_match.group(1))
                    if calls_fixed_match
                    else None
                ),

                "calls_mobile_mn": None,

                "is_unlimited": False,

                "media_type": "fiber",
                "ls_subtype": "ftth",
            }