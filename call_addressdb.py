import psycopg2
import configparser



def call_addressdb(params: dict) -> list:
    """
    Appelle les adresses stockées dans la bdd adresses du serveur vaduz
    pour construire la liste de référence des mots et de leurs coordonnées (x, y)
    renvoi un liste qui prend la forme :
    [
        (code_dossier, nom_dossier, fournisseur), [(MOT1, X, Y), (MOT2, X, Y), ...],
        (code_dossier, nom_dossier, fournisseur), [(MOT1, X, Y), (MOT2, X, Y), ...],
    ]

    Paramaters:
    - postgresql credentials (dict)
    """

    result = []

    conx = psycopg2.connect(**params)
    cursor = conx.cursor()
    sql = "SELECT * from destinations ORDER BY nom "
    # sql = "SELECT * from destinations ORDER BY nom"

    cursor.execute(sql)
    rows = cursor.fetchall()
    for id, code, nom, origine in rows:
        sql = f"SELECT mot, posx, posy FROM coordonnees WHERE destination = {id} ORDER BY posy, posx"
        cursor.execute(sql)
        result.append([(code, nom, origine), cursor.fetchall()])
    
    return result

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf-8')
    params = {
        "host" : config['ADRESSESDB']['HOST'],
        "dbname" : config['ADRESSESDB']['DBNAME'],
        "user" : config['ADRESSESDB']['USER'],
        "password" : config['ADRESSESDB']['password']
    }

    data = call_addressdb(params)
    for item in data:
        print(item)

"""
#     sql = """
# SELECT 
#     destinations.code,
#     destinations.nom,
#     destinations.origine,
#     coordonnees.mot,
#     coordonnees.posx,
#     coordonnees.posy
# FROM destinations
# LEFT JOIN coordonnees 
#     ON destinations.id = coordonnees.destination
# ORDER BY destinations.nom, coordonnees.posy, coordonnees.posx

# """
