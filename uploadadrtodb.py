from pathlib import Path
import psycopg2 
import configparser

config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')
params = {
    "host" : config['ADRESSESDB']['HOST'],
    "dbname" : config['ADRESSESDB']['DBNAME'],
    "user" : config['ADRESSESDB']['USER'],
    "password" : config['ADRESSESDB']['password']
}

addr_path = Path(r"adresses")

conn = psycopg2.connect(**params)
cursor = conn.cursor()


for item in addr_path.iterdir():
    print(item.name)
    nom, code, origine = item.stem.split("_")

    sql = f"insert into destinations (code, nom, origine) values ('{code}', '{nom}', '{origine}') returning id;"
    cursor.execute(sql)
    destid = cursor.fetchone()[0]

    words = []
    with open(item, "r") as f:
        for line in f.readlines():
            word, x, y = line.strip().split("|")
            word = word.replace("'","''")
            sql = f"insert into coordonnees (destination, mot, posx, posy) values ({destid}, '{word}', {int(x)}, {int(y)})"
            cursor.execute(sql)

conn.commit()
conn.close()

        
    # print(words)
    
    # # cursor.execute("select * from destinations")
    # # print(cursor)

    # for word, x, y in words:
