import os
import pandas as pd 
from sqlalchemy import create_engine

from dotenv import load_dotenv
load_dotenv()


class IngestionJSON:

    def __init__(self, dossier):
        self.dossier = dossier
        self.engine = create_engine(
            f"postgresql://{os.getenv('post_user')}:{os.getenv('post_pwd')}@localhost:5435/{os.getenv('post_db_name')}")
    
    def liens_des_fichiers(self):

        listes_des_fichiers = []
        for root, dirs, files in os.walk(self.dossier):
            for file in files:
                if file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    listes_des_fichiers.append(full_path)
        return listes_des_fichiers
    
    def extrait_nom(self, chemin_fichier):
        nom_table = os.path.basename(chemin_fichier).split(".")[0]
        return nom_table
    
    def ingestion(self):
        fichiers = self.liens_des_fichiers()
        for fichier in fichiers:
            nom_table = self.extrait_nom(fichier)
            df = pd.read_json(fichier)
            df.to_sql(nom_table, con=self.engine, if_exists='replace', index=False)
            print(f"Les données du fichier {fichier} ont été insérées dans la table {nom_table}.")


if __name__ == "__main__":
    dossier = "./scraptelecom/scraptelecom/spiders/doc_files" 
    ingestion_json = IngestionJSON(dossier)
    ingestion_json.ingestion()

