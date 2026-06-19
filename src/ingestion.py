import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os 

# environnement
load_dotenv()

post_user = os.getenv("post_user")
post_pwd = os.getenv("post_pwd")
post_db_name = os.getenv("post_db_name")

# Les 5 pays de votre étude
COUNTRIES = {
    "KM": "Comores",
    "MG": "Madagascar",
    "MU": "Mauritius",
    "SN": "Senegal",
    "TZ": "Tanzania"
}

# Codes des indicateurs Banque Mondiale
INDICATORS = {
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "SP.POP.TOTL": "population",
    "NY.GNP.PCAP.CD": "gni_per_capita_usd",      # RNB par habitant
    "SE.ADT.LITR.ZS": "literacy_rate_pct",        # Alphabétisation
    "IT.NET.USER.ZS": "internet_penetration_pct", # Pénétration Internet
    "IT.CEL.SETS": "mobile_subs_per_100"          # Abonnements mobiles/100hab
}

# base de données PostgreSQL
engine = create_engine(f"postgresql://{post_user}:{post_pwd}@localhost:5435/{post_db_name}")


def recup_donnees():
    country_codes = ";".join(COUNTRIES.keys())
    final_data = {code: {"country_name": COUNTRIES[code], "country_code": code} for code in COUNTRIES.keys()}
    
    print(" Interrogation de l'API Banque Mondiale...")
    
    for ind_code, ind_name in INDICATORS.items():

        url = f"https://api.worldbank.org/v2/country/{country_codes}/indicator/{ind_code}?date=2020:2026&format=json&per_page=100"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if len(data) > 1 and data[1]:
                sorted_records = sorted(data[1], key=lambda x: x['date'], reverse=True)
                
                for record in sorted_records:
                    country_iso = record['country']['id']
                    value = record['value']
                    year = record['date']
                    
                    if value is not None and ind_name not in final_data[country_iso]:
                        final_data[country_iso][ind_name] = round(value, 2)
                        final_data[country_iso][f"{ind_name}_year"] = year
                        
        except Exception as e:
            print(f"Erreur API pour {ind_code}: {e}")

    for iso, data in final_data.items():
        if "gni_per_capita_usd" in data:
            data["estimated_monthly_income_usd"] = round(data["gni_per_capita_usd"] / 12, 2)
        else:
            data["estimated_monthly_income_usd"] = None

    df = pd.DataFrame.from_dict(final_data, orient='index')
    print("\n Données socio-économiques récupérées :\n")
    print(df.to_markdown())

    df.to_sql("context_pays", con=engine, if_exists="replace", index=False)
    print("\nDonnées insérées dans la table 'context_pays' de la base de données PostgreSQL.")

if __name__ == "__main__":
    recup_donnees()