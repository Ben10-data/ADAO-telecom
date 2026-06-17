import scrapy
import re 
from datetime import datetime


class YasComoresSpider(scrapy.Spider):
    name = "yas_comores"
    allowed_domains = ["yas.km"]
    
    start_urls = [
    "https://www.yas.km/internet/",
    "https://www.yas.km/dagonet/",
    "https://www.yas.km/dagonet-fibre/",
    "https://www.yas.km/box-yahangu/",
]
    

    ROUTE_MAP = {
        "/internet/":         "parse_internet",
        "/dagonet/":          "parse_dagonet",
        "/dagonet-fibre/":    "parse_dagonet_fibre",
        "/box-yahangu/":      "parse_box_yahangu",
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

# internet mobile 

    def parse_internet(self, response):

        for tab in response.css("div.eael-tab-content-item"):

            tab_id = tab.attrib.get("id", "").replace("-tab", "")

            for card in tab.css("div.card"):

                offer_name = card.css("h3::text").get(default="").strip()

                price_raw = card.css("h4.card-price::text").get(default="").strip()
                price = int(re.sub(r"[^\d]", "", price_raw)) if price_raw else None

                li_texts = [t.strip() for t in card.css("ul li::text").getall() if t.strip()]

                description = " | ".join(li_texts)

                volume = None
                for t in li_texts:
                    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(Go|Mo)", t, re.I)
                    if m:
                        val = float(m.group(1).replace(",", "."))
                        if m.group(2).lower() == "mo":
                            val = round(val / 1000, 3)
                        volume = val
                        break

                validity = None
                for t in li_texts:
                    m = re.search(r"valide\s*(\d+)\s*jour", t, re.I)
                    if m:
                        validity = int(m.group(1))
                        break
                    if "minuit" in t.lower():
                        validity = 1
                        break

                # print({
                #     "tab_id": tab_id,
                #     "offer_name": offer_name,
                #     "price_kmf": price,
                #     "volume_gb": volume,
                #     "validity_days": validity,
                #     "description": description
                # })

                yield {
                        "operator": "YAS Comores",
                        "country": "Comores",
                        "currency": "KMF",
                        "offer_type": "mobile",
                        "source_url": response.url,
                        "scraped_at": datetime.utcnow().isoformat(),
                        "offer_name": offer_name,
                        "price_local": float(price) if price is not None else None,
                        "data_volume_gb": volume,
                        "speed_mbps": None,
                        "validity_days": validity,
                        "install_fee": None,
                        "equipment_fee": None,
                        "calls_fixed": None,
                        "calls_mobile_mn": None,
                        "is_unlimited": False,
                        "media_type": "mobile",
                        "ls_subtype": tab_id if tab_id else None,
                    }
                
    
    # pour le dagonet et dagonet fibre 
    def parse_dagonet(self, response):

        for tbody in response.css("tbody"):

            for tr in tbody.css("tr"):

                tds = [td.css("::text").get(default="").strip() for td in tr.css("td")]

                if len(tds) < 4:
                    continue

                offer_name = tds[0]

                price_raw = tds[1]
                price = float(re.sub(r"[^\d]", "", price_raw)) if price_raw else None

            
                # -------------------------
                speed_mbps = None
                m_speed = re.search(r"(\d+(?:\.\d+)?)\s*Mbps", " ".join(tds))
                if m_speed:
                    speed_mbps = float(m_speed.group(1))

                # -------------------------
                data_volume_gb = None
                if "illimité" in " ".join(tds).lower():
                    data_volume_gb = None
                else:
                    m_vol = re.search(r"(\d+(?:\.\d+)?)\s*GB", " ".join(tds), re.I)
                    if m_vol:
                        data_volume_gb = float(m_vol.group(1))

                # -------------------------
                validity_days = None
                m_val = re.search(r"(\d+)\s*jour", " ".join(tds), re.I)
                if m_val:
                    validity_days = int(m_val.group(1))

                yield {
                    "operator": "Yas Comores",
                    "country": "Comores",
                    "currency": "KMF",
                    "offer_type": "fiber",
                    "source_url": response.url,
                    "scraped_at": datetime.utcnow().isoformat(),

                    "offer_name": offer_name,
                    "price_local": price,

                    "data_volume_gb": data_volume_gb,
                    "speed_mbps": speed_mbps,

                    "validity_days": validity_days,

                    "install_fee": None,
                    "equipment_fee": None,

                    "calls_fixed": None,
                    "calls_mobile_mn": None,

                    "is_unlimited": True if data_volume_gb is None else False,

                    "media_type": "fiber",
                    "ls_subtype": "dagonet"
                }

    def parse_dagonet_fibre(self, response):
        

        for row in response.css("tbody tr"):

            tds = [
                td.css("::text").get(default="").strip()
                for td in row.css("td")
            ]

            if len(tds) < 5:
                continue

            offer_name = tds[0]

            description = tds[1]

            # Vitesse
            speed_mbps = None
            m = re.search(r"(\d+)\s*Mbps", description, re.I)
            if m:
                speed_mbps = float(m.group(1))

            # Volume
            data_volume_gb = None
            m = re.search(r"(\d+)\s*Go", description, re.I)
            if m:
                data_volume_gb = float(m.group(1))

            # Prix mensuel
            price_local = None
            m = re.search(r"([\d\s]+)", tds[3])
            if m:
                price_local = float(
                    re.sub(r"\D", "", m.group(1))
                )

            # Frais d'installation
            install_fee_kmf = None
            m = re.search(r"([\d\s]+)", tds[4])
            if m:
                install_fee_kmf = float(
                    re.sub(r"\D", "", m.group(1))
                )

            yield {
                "operator": "YAS Comores",
                "country": "Comores",
                "currency": "KMF",
                "offer_type": "fiber",
                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),

                "offer_name": offer_name,
                "price_local": price_local,

                "data_volume_gb": data_volume_gb,
                "speed_mbps": speed_mbps,

                "validity_days": 30,

                "install_fee": install_fee_kmf,
                "equipment_fee": None,

                "calls_fixed": None,
                "calls_mobile_mn": None,

                "is_unlimited": False,

                "media_type": "fiber",

                "ls_subtype": None,
            }

    def parse_box_yahangu(self, response):

        for card in response.css("div.eael-tabs-content div.card"):
            offer_name = card.css("h3::text").get(default="").strip()
            price_raw = card.css("h4.card-price::text").get(default="").strip()
            price = int(re.sub(r"[^\d]", "", price_raw)) if price_raw else None
            description = " | ".join(t.strip() for t in card.css("ul li::text").getall() if t.strip())

            speed_mbps = None
            m_speed = re.search(r"(\d+(?:\.\d+)?)\s*Mbps", description, re.I)
            if m_speed:
                speed_mbps = float(m_speed.group(1))

            data_volume_gb = card.css("ul li::text").getall()[0]
            data_volume_gb = int(re.sub(r"\D", "", data_volume_gb)) if data_volume_gb else None

            validity_days = None
            m_val = re.search(r"(\d+)\s*jour", description, re.I)
            if m_val:
                validity_days = int(m_val.group(1))

            yield {
                "operator": "YAS Comores",
                "country": "Comores",
                "currency": "KMF",
                "offer_type": "fixed_wireless",
                "source_url": response.url,
                "scraped_at": datetime.utcnow().isoformat(),
                "offer_name": offer_name,
                "price_local": price,
                "data_volume_gb": data_volume_gb,
                "speed_mbps": speed_mbps,
                "validity_days": validity_days,
                "install_fee": None,
                "equipment_fee": None,
                "calls_fixed": None,
                "calls_mobile_mn": None,
                "is_unlimited": False,
                "media_type": "4G+/5G",
                "ls_subtype": None,
            }

            