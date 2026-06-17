import scrapy
import re
from datetime import datetime


class ComoresTelecomSpider(scrapy.Spider):
    name = "comores_telecom"
    allowed_domains = ["comorestelecom.km"]
    start_urls = [
        "https://www.comorestelecom.km/portail/offres/mobile/15/",
        "https://www.comorestelecom.km/portail/offres/2/",
        "https://www.comorestelecom.km/portail/offres/3/",
        "https://www.comorestelecom.km/portail/offres/18/",
    ]

    # Routing URL → méthode parse dédiée
    ROUTE_MAP = {
        "/offres/mobile/15/": "parse_mobile",
        "/offres/2/":         "parse_ls",
        "/offres/3/":         "parse_adsl",
        "/offres/18/":        "parse_fibre",
    }

    def parse(self, response):
        # Déterminer quelle méthode appeler selon l'URL
        method_name = next(
            (v for k, v in self.ROUTE_MAP.items() if k in response.url),
            None
        )
        if method_name:
            yield from getattr(self, method_name)(response)
        else:
            self.logger.warning(f"URL non routée : {response.url}")

    # ------------------------------------------------------------------
    # MOBILE — /offres/mobile/15/
    # ------------------------------------------------------------------
    def parse_mobile(self, response):
        for card in response.css("div.pricing-table"):

            offer_name = card.css("h5::text").get(default="").strip()
            price_raw  = card.css("div.card > h3::text").get(default="").strip()

                    # Volume internet 
            volume_texts = [
                    t.strip()
                    for t in card.css("h3::text, p strong::text").getall()
                    if t.strip()
                ]
                    
            volume_text = volume_texts[1]

            valid_day = card.css("ul li::text").getall()[0]

            #print(f"test - offer: {offer_name}, price: {price_raw}, volume_text: {volume_text} validity: {valid_day}")
                
    
        

            yield {
                "operator":          "Comores Telecom",
                "country":           "Comores",
                "currency":          "KMF",
                "offer_type":        "mobile",
                "source_url":        response.url,
                "scraped_at":        datetime.utcnow().isoformat(),
                "offer_name":        offer_name,
                "price_local":       self._parse_price(price_raw),
                "data_volume_gb":    self._extract_volume(volume_text),
                "speed_mbps":        None,
                "validity_days":     self._extract_validity(valid_day),
                "install_fee":   None,
                "equipment_fee": None,
                "calls_fixed":       None,
                "calls_mobile_mn":   None,
                "is_unlimited":      False,
                "media_type":        None,
                "ls_subtype":        None,
            }

    # ------------------------------------------------------------------
    # LIAISONS SPÉCIALISÉES — /offres/2/
    # ------------------------------------------------------------------
    def parse_ls(self, response):
        for card in response.css("div.pricing-table"):

            offer_name = card.css("h5::text").get(default="").strip()
            price_raw  = card.css("div.card > h3::text").get(default="").strip()

            # Débit extrait depuis le nom : "LS cuivre 1 MB/S", "LS fibre 20 Mb/s"
            speed_mbps = self._extract_speed_from_name(offer_name)

            # Support : cuivre ou fibre
            media_type = "fiber" if "fibre" in offer_name.lower() else "copper"

            # Sous-type LS
            name_lower = offer_name.lower()
            if "inter" in name_lower:
                ls_subtype = "inter_urban_inter_island"
            elif "urbain" in name_lower:
                ls_subtype = "urban"
            else:
                ls_subtype = "standard"

            # frais d'equipement et installation 
            frais_inst_equip = []
            import re

            frais_inst_equip = []

            for li in card.css("ul li::text").getall():
                montant = re.search(r"(\d+)\s*kmf", li, re.I)
                if montant:
                    frais_inst_equip.append(montant.group(1))
            
            if len(frais_inst_equip) == 2:
                frais_installation = frais_inst_equip[0]
                frais_equipement = frais_inst_equip[1]
            elif len(frais_inst_equip) == 1:
                frais_installation = None 
                frais_equipement = frais_inst_equip[0]
            else:
                frais_installation = None
                frais_equipement = None
                


            #print(f"test - offer: {offer_name}, price: {price_raw}, speed: {speed_mbps} Mbps media: {media_type} subtype: {ls_subtype}")

            yield {
                "operator":          "Comores Telecom",
                "country":           "Comores",
                "currency":          "KMF",
                "offer_type":        "ligne_speciale",
                "source_url":        response.url,
                "scraped_at":        datetime.utcnow().isoformat(),
                "offer_name":        offer_name,
                "price_local":       self._parse_price(price_raw),
                "data_volume_gb":    None,
                "speed_mbps":        speed_mbps,
                "validity_days":     None,
                "ussd_code":         None,
                "install_fee":   frais_installation,
                "equipment_fee": frais_equipement,
                "calls_fixed":       None,
                "calls_mobile_mn":   None,
                "is_unlimited":      True,
                "media_type":        media_type,
                "ls_subtype":        ls_subtype,
            }

    # ------------------------------------------------------------------
    # ADSL — /offres/3/
    # ------------------------------------------------------------------
    def parse_adsl(self, response):
        for card in response.css("div.pricing-table"):

            offer_name = card.css("h5::text").get(default="").strip()
            price_raw  = card.css("div.card > h3::text").get(default="").strip()

            # Débit 
            speed_raw = card.css("h3::text").getall()[1]

            # frais d'installation 
            li_install = card.css("ul li::text").get(default="")
            montant_install = re.search(r"(\d+)\s*kmf", li_install, re.I)
            frais_installation = montant_install.group(1) if montant_install else None


            yield {
                "operator":          "Comores Telecom",
                "country":           "Comores",
                "currency":          "KMF",
                "offer_type":        "adsl",
                "source_url":        response.url,
                "scraped_at":        datetime.utcnow().isoformat(),
                "offer_name":        offer_name,
                "price_local":       self._parse_price(price_raw),
                "data_volume_gb":    None,
                "speed_mbps":        self._extract_speed(speed_raw),
                "validity_days":     None,
                "ussd_code":         None,
                "install_fee":   frais_installation,
                "equipment_fee": None,
                "calls_fixed":       None,
                "calls_mobile_mn":   None,
                "is_unlimited":      True,
                "media_type":        "copper",
                "ls_subtype":        None,
            }

    # ------------------------------------------------------------------
    # FIBRE NEMA NET — /offres/18/
    # ------------------------------------------------------------------
    def parse_fibre(self, response):
        for card in response.css("div.pricing-table"):

            offer_name = card.css("h5::text").get(default="").strip()
            price_raw  = card.css("div.card > h3::text").get(default="").strip()

            # Tout le texte des <li>
         
            data = []

            for li in card.css("ul li"):
                texte = " ".join(
                    t.strip()
                    for t in li.css("::text").getall()
                    if t.strip()
                )
                texte = texte.replace("\xa0", " ")
                data.append(texte)




            yield {
                "operator":          "Comores Telecom",
                "country":           "Comores",
                "currency":          "KMF",
                "offer_type":        "fixed_wireless",
                "source_url":        response.url,
                "scraped_at":        datetime.utcnow().isoformat(),
                "offer_name":        offer_name,
                "price_local":       self._parse_price(price_raw),
                "data_volume_gb":    self._extract_volume(data[2]),
                "speed_mbps":        self._extract_speed(data[1]),
                "validity_days":     self._extract_validity(data[2]),
                "ussd_code":         None,
                "install_fee":   None,
                "equipment_fee": None,
                "calls_fixed":       self._extract_calls_fixed(data[3]),
                "calls_mobile_mn":   self._extract_calls_mobile(data[4]),
                "is_unlimited":      False,
                "media_type":        "wttx_5g",
                "ls_subtype":        None,
            }

    # ------------------------------------------------------------------
    # Helpers partagés
    # ------------------------------------------------------------------
    def _parse_price(self, raw):
        cleaned = re.sub(r"[^\d]", "", raw)
        return float(cleaned) if cleaned else None

    def _extract_volume(self, text):
        m = re.search(r"(\d+)\s*Go", text, re.IGNORECASE)
        if m:
            return float(m.group(1))
        m = re.search(r"(\d+)\s*Mo", text, re.IGNORECASE)
        if m:
            return round(float(m.group(1)) / 1000, 4)
        return None

    def _extract_speed(self, text):
        m = re.search(r"(\d+)\s*Mb[/\s]?s", text, re.IGNORECASE)
        if m:
            return float(m.group(1))
        m = re.search(r"(\d+)\s*Kb[/\s]?s", text, re.IGNORECASE)
        if m:
            return round(float(m.group(1)) / 1000, 4)
        return None

    def _extract_speed_from_name(self, name):
        m = re.search(r"(\d+)\s*[Mm][Bb]", name)
        return float(m.group(1)) if m else None

    def _extract_validity(self, text):
        m = re.search(r"(\d+)\s*jours?", text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)\s*heu?r?e?s?", text, re.IGNORECASE)
        if m:
            return max(1, round(int(m.group(1)) / 24))
        return None


    def _extract_calls_fixed(self, text):
        if re.search(r"fixe.{0,10}illimit", text, re.IGNORECASE):
            return "unlimited"
        return None

    def _extract_calls_mobile(self, text):
        m = re.search(r"(\d+)\s*mn", text, re.IGNORECASE)
        return int(m.group(1)) if m else None