import os
import requests
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

class API_ACD():
    def __init__(self, url, username, password):
        """
        Première connexion pour obtenir le UUID
        """
        self.url = url
        self.conx_ok = False
        self.select = False

        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json"
        }
        payload = {
            "CNX": "CNX",
            "Identifiant": username,
            "MotDePasse": password
        }
        url = f"{self.url}/authentification"
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            self.uuid = r.json()["UUID"]
            self.conx_ok = True
            logging.info("Authentification OK")
        else:
            logging.error("connection failed")
        
    def select_dossier(self, code_dossier):
        """
        Sélection du dossier
        """

        headers = {
            "Accept" : "application/json",
            "CNX" : "CNX",
            "UUID" : self.uuid,
        }
        url = f"{self.url}/sessions/dossier/{code_dossier}"
        r = requests.post(url, headers=headers)
        if r.status_code == 200:
            self.select = True
        else:
            logging.error("Echec sélection dossier")

    def push_paniere(self, file, doc_name):

        headers = {
            "CNX" : "CNX",
            "UUID" : self.uuid,
        }
        files = {"file": (f"{doc_name}",file)}
        form = {"type" : 1}
        url = f"{self.url}/panieres/documents"
        r = requests.post(url, headers=headers, files=files, data=form)
        if r.status_code in (200, 201):
            self.select = True
        else:
            logging.error("Echec envoi document")
            print(r.json())
        


if __name__ == "__main__":
    url = 'https://comptoir.newtonexpertise.com/iSuiteExpert/api/v1'
    username = "nro@newtonexpertise.com"
    password = "vocifere1414"

    doc = r"C:\Users\nicolas\Documents\alien.pdf"

    acd = API_ACD(url, username, password) 
    print(acd.uuid) 
    if acd.conx_ok:
        acd.select_dossier("FORMACLI")
        if acd.select:
            print("dossier sélectionné")
    
    with open(doc, "rb") as f:
        acd.push_paniere(f, "alien.pdf")

    # acd.push_doc_paniere(acd.uuid, doc, 1, )

    
    # curl -X POST --header 'Content-Type: multipart/form-data' --header 'Accept: application/json' --header 'CNX: CNX' --header 'UUID: 86PKH1K00AL0SSETC3287F2SIPT45N' -F type=0 -F   'http://tunis.axe.lan/iSuiteExpert/api/v1/panieres/documents'
    


# {"document":{"id":0,"nom":"BRINKS-2024-09-01--319,01 E","type":{"idId":1,"sLibelle":"Fact. Achat","bDefaut":true,"inbDoc":0,"iTailleDocMax":20971520,"isFamilleFacture":true,"famille":"_TYPE_FACTURES_ACHAT","extensionsAutorisees":"","documents":[],"iTailleDocMaxFormatted":"20 Mo","extensionsAutoriseesArray":[]},"extension":"PDF","commentaire":"bouh!","factureunique":false,"datedepot":false},"forceDoublon":false}
