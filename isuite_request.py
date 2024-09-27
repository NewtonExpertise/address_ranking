import os
import requests
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

class ISuiteRequest():
    def __init__(self, url: str, username: str, password: str) -> None:
        """
        Dès qu'une nouvelle instance est créée on se conencte au portail
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
        
    def select_dossier(self, code_dossier: str) -> None:
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

    def push_paniere(self, file: bytes, doc_name: str) -> None:
        """
        Envoi d'un document dans la panière. Un dossier devra être sélectionné avant
        avec select_dossier. Type : 1 correspond au type Achat
        """

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


if __name__ == "__main__":
    url = 'https://comptoir.newtonexpertise.com/iSuiteExpert/api/v1'
    username = "nro@newtonexpertise.com"
    password = "vocifere1414"

    doc = r"C:\Users\nicolas\Documents\FACTURE TYPE WD NICOLAS ROLLET 290124 au 010224 Garden BKG.pdf"

    isuite = ISuiteRequest(url, username, password) 

    if not isuite.conx_ok:
        print("Echec authentification")

    isuite.select_dossier("FORMACLI")

    if not isuite.select:
        print("Echec sélection dossier")
    
    with open(doc, "rb") as f:
        isuite.push_paniere(f, "facture.pdf")
