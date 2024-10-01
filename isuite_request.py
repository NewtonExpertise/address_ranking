import requests

class ISuiteRequest():
    """
    Instance de communication avec les API ACD iSuite
    """
    def __init__(self, url: str, username: str, password: str) -> None:
        """
        Dès qu'une nouvelle instance est créée on tente une connexion au portail
        On récupère le UUID pour autoriser les requêtes suivantes
        """
        self.url = url
        self.conx_ok = False
        self.select = False
        self.depot = False
        self.response = ""

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
        self.response = r.json()
        if r.status_code == 200:
            self.uuid = r.json()["UUID"]
            self.conx_ok = True
        
    def select_dossier(self, code_dossier: str) -> None:
        """
        Sélection du dossier. Obligatoire pour agir sur la panière
        """

        headers = {
            "Accept" : "application/json",
            "CNX" : "CNX",
            "UUID" : self.uuid,
        }
        url = f"{self.url}/sessions/dossier/{code_dossier}"
        r = requests.post(url, headers=headers)
        self.response = r.json()            
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
        self.response = r.json()                
        if r.status_code in (200, 201):
            self.depot = True 



