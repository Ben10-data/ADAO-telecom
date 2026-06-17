import re
import scrapy
from datetime import datetime 


class YasTanzaniaSpider(scrapy.Spider):
    name = "yas_tanzania"
    allowed_domains = ["yas.co.tz"]

    start_urls = [
        "https://yas.co.tz/fiber-home/",
        "https://yas.co.tz/consumer/mobile-plans/internet/",
        "https://yas.co.tz/consumer/home-plans/5g-home-plan/",
    ]

    ROUTE_MAP = {
        "/fiber-home/": "parse_fiber_home",
        "/consumer/mobile-plans/internet/": "parse_internet",
        "/consumer/home-plans/5g-home-plan/": "parse_home_5g",
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
    # FIBER HOME
    # =========================
    def parse_fiber_home(self, response):

        cards = response.css("div.swiper.offers-slider .swiper-slide .card")

        for card in cards:

            title = card.css("h5::text").get(default="").strip()

            # prix + sous-titre plan
            h3_texts = [
                t.strip()
                for t in card.css("h3::text").getall()
                if t.strip()
            ]

            price_raw = h3_texts[0] if len(h3_texts) > 0 else ""
            plan_speed = h3_texts[1] if len(h3_texts) > 1 else ""

            # recuperation des li 
            features = [
                t.strip()
                for t in card.css("ul li::text").getall()
                if t.strip()
            ]
            # nombre de jours de validité
            validity = re.search(r"\s*(\d+)\s*", features[3], re.I).group(1)

            speed_match = re.search(r"(\d+)\s*Mbps", plan_speed, re.I)
            speed_mbps = int(speed_match.group(1)) if speed_match else None

            is_unlimited = any(
                "unlimited" in feature.lower()
                for feature in features
            )
                        

            yield {
                "operator":          "YAS Tanzania",
                "country":           "Tanzania",
                "currency":          "TZS",
                "offer_type":        "fiber",
                "source_url":        response.url,
                "scraped_at":        datetime.utcnow().isoformat(),

                "offer_name":        title,
                "price_local":       float(price_raw.replace(",", "")) if price_raw else None,

                "data_volume_gb":    None,
                "speed_mbps":        speed_mbps,
                "validity_days":     int(validity) if validity else None,

                "install_fee":   None,
                "equipment_fee": None,
                "calls_fixed":       None,
                "calls_mobile_mn":   None,
                "is_unlimited":      is_unlimited,
                "media_type":        "fiber",
                "ls_subtype":        "ftth",
            }
        
    # =========================

    def parse_internet(self, response):

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

            # volume
            volume_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(GB|MB)",
                offer_name,
                re.I
            )

            volume_text = volume_match.group(0) if volume_match else None
            if volume_text and "MB" in volume_text:
                volume_text = round(float(volume_text.replace("MB", "").strip()) / 1024, 2)
            else: 
                volume_text = float(volume_text.replace("GB", "").strip()) if volume_text else None

            # validité
            validity_text = next(
                (f for f in features if "valid" in f.lower()),
                ""
            )

            validity_days = None

            if "24h" in validity_text.lower():
                validity_days = 1

            else:
                match = re.search(r"(\d+)\s*days?", validity_text, re.I)

                if match:
                    validity_days = int(match.group(1))

                else:
                    match = re.search(r"(\d+)\s*months?", validity_text, re.I)

                    if match:
                        validity_days = int(match.group(1)) * 30


            yield {
                "operator":          "YAS Tanzania",
                "country":           "Tanzania",
                "currency":          "TZS",
                "offer_type":        "mobile",
                "source_url":        response.url,
                "scraped_at":        datetime.utcnow().isoformat(),

                "offer_name":        offer_name,
                "price_local":       float(price_raw.replace(",", "")) if price_raw else None,

                "data_volume_gb":    volume_text,
                "speed_mbps":        None,
                "validity_days":     validity_days,

                "install_fee":   None,
                "equipment_fee": None,
                "calls_fixed":       None,
                "calls_mobile_mn":   None,

                "is_unlimited":      False,
                "media_type":        "mobile_data",
                "ls_subtype":        None,
            }

# home 5G
    def parse_home_5g(self, response):

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

            speed_match = re.search(
                r"(\d+)\s*Mbps",
                offer_name,
                re.I
            )

            speed_mbps = (
                int(speed_match.group(1))
                if speed_match
                else None
            )

            is_unlimited = any(
                "unlimited" in feature.lower()
                for feature in features
            )



            yield {
                "operator":          "YAS Tanzania",
                "country":           "Tanzania",
                "currency":          "TZS",
                "offer_type":        "home_5g",
                "source_url":        response.url,
                "scraped_at":        datetime.utcnow().isoformat(),

                "offer_name":        offer_name,
                "price_local":       float(price_raw.replace(",", "")) if price_raw else None,

                "data_volume_gb":    None,
                "speed_mbps":        speed_mbps,
                "validity_days":     None,

                "install_fee":   None,
                "equipment_fee": None,
                "calls_fixed":       None,
                "calls_mobile_mn":   None,

                "is_unlimited":      is_unlimited,

                "media_type":        "5g",
                "ls_subtype":        "home_5g",
            }