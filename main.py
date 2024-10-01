import os
import math
import logging
import configparser
import shutil
from datetime import datetime
from pathlib import Path
from pdf_to_image import pdf_to_image
from ocerize import ocr_extract_and_order_words
from isuite_request import ISuiteRequest
from call_addressdb import call_addressdb


# logging.basicConfig(
#     format='%(asctime)s-%(module)s \t %(levelname)s - %(message)s',
#     level="INFO",
#     encoding="cp1252"
# )

logging.basicConfig(
    filename= f"./log/traces.log",
    filemode="w",
    format='%(asctime)s-%(module)s \t %(levelname)s - %(message)s',
    level="INFO",
    encoding="cp1252"
)



def calc_distance(coord1, coord2):
    """
    Calcul de la distance euclidienne entre deux coordonnées

    parameters:
    coord1 : int tuple
    coord2 : int tuple

    returns:
    distance as float value
    """
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def build_address_book(source: Path) -> list:
    """
    Collecte tous les fichiers .coord de la source pour 
    retourner la listes des coordonnées de chaque mot
    """
    book = []
    for file in source.iterdir():
        name = file.stem
        coord_list = []
        with open(file, "r") as f:
            lines = f.readlines()
        for line in lines:
            w, x, y = line.strip().split("|")
            coord_list.append((w, int(x), int(y)))
        book.append((name, coord_list))  
    return book  

def calc_match_ratio(candidates: list, trial: list, drift: int = 0) -> float:
    """
    Recherche le nombre de mots communs entre les deux listes
    Vérifie si :
    - chaque mot est présent
    - si ses coordonnées sont à une distance proche de 0
    Si OK, renvoi un ratio de correspondance

    Parameters 
    - candidates : mots à évaluer
    - trial: mots de référence
    - drift : marge d'erreur de la distance en les deux mots (en pixel)

    Return
    - float
    """
    ratio = 0.
    matches = []
    for can_w, can_x, can_y in candidates:
        for tri_w, tri_x, tri_y in trial:
            if can_w == tri_w:
                distance = calc_distance((can_x, can_y), (tri_x, tri_y))
                if distance <= drift:
                    matches.append((can_w, can_x, can_y))
    if matches:
        ratio = len(matches) / len(trial)
    return ratio

def propose_winner(candidate_words: list, address_db: list) -> tuple :
    """
    Va comparer la liste de mots/coordonnées du document analyse avec la base d'adresses
    Le gagnant est celui qui retourne le meilleur ratio calculé par cal_match_ratio, mais
    à condition que celui-ci soit supérieur à 90%.
    Avec une moyenne de 12 mots par adresses, ça permet une tolérance d'un mot non matché
    La fonction renvoi deux éléments:
    - winner (tuple)
    - le classement des 5 meilleurs ratio (pour analyse en cas de problème)

    Parameters:
    - candidate_words : liste des mots du document à évaluer
    - address_db = listes les mots de la base adresses
    """
    ranking = []
    winner = None

    for (code, nom, origine), test_words in address_db:
        ratio = calc_match_ratio(candidate_words, test_words, drift=10)
        if ratio >= 0.2:
            ranking.append((ratio, code, nom, origine))
    if ranking:
        ranking = sorted(ranking, reverse=True)[:5] 
        if ranking[0][0] >= 0.9:
            winner = ranking[0][1:]

    return winner, ranking


def trace_envoi_paniere(nameparts: list) -> None:
    timestamp = [datetime.now().strftime("%Y-%m-%d %H:%M")]
    timestamp += nameparts
    line = " ".join(timestamp)
    logfile = LOG_DIR / "envois_paniere.log"
    try:
        with open(logfile, "a") as f:
            f.write(line)
            f.write("\n")
    except IOError as e:
        logging.error(f"{logfile} inaccessible")


#####################################################################


config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')
PDF_DIR = Path(config['PATHS']['PDF_DIR'])
IDENT_DIR = Path(config['PATHS']['IDENT_DIR'])
FAIL_DIR = Path(config['PATHS']['FAIL_DIR'])
LOG_DIR = Path(config['PATHS']['LOG_DIR'])

if not PDF_DIR.is_dir():
    PDF_DIR.mkdir(parents=True)
if not IDENT_DIR.is_dir():
    IDENT_DIR.mkdir(parents=True)
if not LOG_DIR.is_dir():
    LOG_DIR.mkdir(parents=True)

# IS_USR = config['ISUITE']['USERNAME']
# IS_PWD = config['ISUITE']['PASSWORD']
# IS_URL = config['ISUITE']['URL']
db_params = {
    "host" : config['ADRESSESDB']['HOST'],
    "dbname" : config['ADRESSESDB']['DBNAME'],
    "user" : config['ADRESSESDB']['USER'],
    "password" : config['ADRESSESDB']['password']
}

address_db = call_addressdb(db_params)

if not address_db:
    logging.critical("Base de données adresses vide !")
    exit()

for pdf in PDF_DIR.iterdir():

    if not pdf.name.endswith(".pdf"):
        continue

    logging.info(f"============{pdf.name}==================")
    print(f"============{pdf.name}==================")
    
    image = pdf_to_image(pdf)
    candidates = ocr_extract_and_order_words(image)
    
    winner, ranking = propose_winner(candidates, address_db)
    
    for i, rank in enumerate(ranking, start=1):
        logging.info(f"{i}, {rank}")
    
    if not winner:
        logging.warning(f"Aucune adresse ne correspond à {pdf.name}")
        shutil.move(pdf, PDF_DIR / "echec" / pdf.name)
        continue
    else:
        code, nom, origine = winner
        timestamp = datetime.now().strftime("%Y%m%d")
        logging.info(f"dossier proposé : {nom}, ({code})")

        shutil.move(pdf, IDENT_DIR / f"{code}_{nom}_{origine}_{timestamp}.pdf")

    #### Envoi paniere ################################

    # isuite = ISuiteRequest(IS_URL, IS_USR, IS_PWD)
    # isuite.select_dossier("FORMACLI")

    # if not isuite.select:
    #     logging.error(f"Echec connexion {isuite.response}")

    # with open(pdf, "rb") as f:
    #     isuite.push_paniere(f, f"{vendor}-{dossier}.pdf")

    # if isuite.depot:
    #     logging.info("Envoi panière OK")
    #     trace_envoi_paniere([vendor, dossier, pdf.name])
    #     shutil.move(pdf, PDF_DIR / "envoyes" / pdf.name)
    # else:
    #     logging.error("Echec envoi panière")
    #     logging.error()
    #     shutil.move(pdf, PDF_DIR / "echec" / pdf.name)


