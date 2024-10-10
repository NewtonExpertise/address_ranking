import psycopg2
import logging


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
    try:
        conx = psycopg2.connect(**params)
    except psycopg2.OperationalError as e:
        logging.critical(f"bdd adresses inaccessible : {e}")
        return result
    cursor = conx.cursor()
    sql = "SELECT * from destinations ORDER BY nom "
    cursor.execute(sql)
    rows = cursor.fetchall()
    for id, code, nom, origine in rows:
        sql = f"SELECT mot, posx, posy FROM coordonnees WHERE destination = {id} ORDER BY posy, posx"
        cursor.execute(sql)
        result.append([(code, nom, origine), cursor.fetchall()])
    
    return result

# if __name__ == "__main__":

#     import configparser
#     config = configparser.ConfigParser()
#     config.read("config.ini", encoding='ansi')
#     db_params = {
#     "host" :   config['ADRESSESDB']['HOST'],
#     "dbname" : config['ADRESSESDB']['DBNAME'],
#     "user" :   config['ADRESSESDB']['USER'],
#     "password" : config['ADRESSESDB']['password']
#     }
#     rows = call_addressdb(params=db_params)
#     [print(x) for x in rows]