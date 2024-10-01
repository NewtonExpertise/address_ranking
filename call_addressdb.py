import psycopg2


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
    cursor.execute(sql)
    rows = cursor.fetchall()
    for id, code, nom, origine in rows:
        sql = f"SELECT mot, posx, posy FROM coordonnees WHERE destination = {id} ORDER BY posy, posx"
        cursor.execute(sql)
        result.append([(code, nom, origine), cursor.fetchall()])
    
    return result
