import os
import requests
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

class ISuiteRequest():
    def __init__(self, url, username, password):
        """
        Première connexion pour obtenir le UUID
        """
        self.url = url
        self.conx_ok = False
        self.select = False
        self.depot = False

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
        else:
            logging.debug(r.json())
        
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
            self.depot = True
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
