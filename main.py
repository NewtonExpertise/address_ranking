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

timestamp = datetime.now().strftime("%Y-%m-%d %H%M")
logging.basicConfig(
    filename= f"./log/traces {timestamp}.log",
    filemode="a",
    format='%(asctime)s %(module)10s %(funcName)15s %(levelname)7s : %(message)s',
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
            if can_w.lower() == tri_w.lower():
                distance = calc_distance((can_x, can_y), (tri_x, tri_y))
                if distance <= drift:
                    matches.append((can_w, can_x, can_y))
    if matches:
        ratio = len(matches) / len(trial)
    return ratio, matches

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
        ratio, matches = calc_match_ratio(candidate_words, test_words, drift=10)
        if ratio >= 0.2:
            ranking.append((ratio, code, nom, origine, matches))
    if ranking:
        ranking = sorted(ranking, reverse=True)[:5] 
        if ranking[0][0] >= 0.9:
            winner = ranking[0][1:]


    return winner, ranking


#####################################################################
#####################################################################

config = configparser.ConfigParser()
try:
    config.read("config.ini", encoding='ansi')
    logging.info("")
    logging.info("---- START -----")
    logging.info("")
    logging.info("chargement config.ini OK")
except:
    logging.critical(f"Config.ini absent !")
    exit()
    
PDF_DIR   = Path(config['PATHS']['PDF_DIR'])
IDENT_DIR = Path(config['PATHS']['IDENT_DIR'])
FAIL_DIR  = Path(config['PATHS']['FAIL_DIR'])
SENT_DIR  = Path(config['PATHS']['SENT_DIR'])
IS_USR    = config['ISUITE']['USERNAME']
IS_PWD    = config['ISUITE']['PASSWORD']
IS_URL    = config['ISUITE']['URL']

db_params = {
    "host" :   config['ADRESSESDB']['HOST'],
    "dbname" : config['ADRESSESDB']['DBNAME'],
    "user" :   config['ADRESSESDB']['USER'],
    "password" : config['ADRESSESDB']['password']
}

TESTMODE = False
if (config['DEFAULT']['TESTMODE']) == "1":
    TESTMODE = True
    logging.warning("TESTMODE est actif !")

for i, target in enumerate((PDF_DIR, IDENT_DIR, FAIL_DIR, SENT_DIR)):
    logstr = f"{i}. Chemin : {str(target)}"
    if not target.is_dir():
        target.mkdir(parents=True)
        logstr += " (CREE)"
    else:
        logstr += " (OK)"
    logging.info(logstr)


#### Identification des documents ################################

address_db = call_addressdb(db_params)

if not address_db:
    logging.critical("Base de données adresses vide !")
    exit()
else:
    logging.info(f"nombres d'adresses chargees : {len(address_db)}")

for pdf in PDF_DIR.iterdir():

    if not pdf.name.endswith(".pdf"):
        continue
    
    banner = "======={}{}".format(pdf.name, "="*(60-len(pdf.name)))
    logging.info(banner)
    print(banner)
    
    image = pdf_to_image(pdf, keep_png=TESTMODE)
    candidates = ocr_extract_and_order_words(image)
    
    winner, ranking = propose_winner(candidates, address_db)
    
    for i, rank in enumerate(ranking, start=1):
        logging.info(f"{i}, {rank}")
    
    if not winner:
        logging.warning(f"Aucune adresse ne correspond a {pdf.name}")
        if not TESTMODE:
            shutil.move(pdf, FAIL_DIR / pdf.name)
        continue

    code, nom, origine, words = winner
    timestamp = datetime.now().strftime("%Y%m%d-%H%M-%f")
    logging.info(f"dossier propose : {nom}, ({code})")
    print(words)

    # if not TESTMODE:
    shutil.move(pdf, IDENT_DIR / f"{code}_{nom}_{origine}_{timestamp}.pdf")

#### Envoi paniere ################################

for pdf in IDENT_DIR.iterdir():


    if not pdf.suffix == ".pdf":
        continue

    parts = pdf.stem.split("_")
    if len(parts) == 4:
        code, nom, origine, stamp = parts
    else:
        continue

    # Exception pour dégager les dossiers affectés au code PASCLIENT
    # (resto accessible depuis le portail mais pas client du cabinet)
    if code == "PASCLIENT":
        os.remove(str(pdf))
        logging.warning(f"suppression de non-client : {pdf.name}")
        continue

    if not TESTMODE:
        isuite = ISuiteRequest(IS_URL, IS_USR, IS_PWD)
        isuite.select_dossier(code)

        if not isuite.select:
            logging.error(f"Echec connexion {isuite.response}")
        with open(pdf, "rb") as f:
            isuite.push_paniere(f, f"{origine}-{nom}-{stamp}.pdf")

        if isuite.depot:
            logging.info(f"dépôt de {origine}-{nom}-{stamp}.pdf")
            shutil.move(pdf, SENT_DIR / pdf.name)
        else:
            logging.error(f"Echec envoi panière : {pdf.name}")