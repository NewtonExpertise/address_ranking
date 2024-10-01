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


formatter = logging.Formatter('%(asctime)s-%(module)s \t %(levelname)s - %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file, mode="w")        
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


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


#####################################################################
#####################################################################


config = configparser.ConfigParser()
config.read("config.ini", encoding='ansi')
PDF_DIR = Path(config['PATHS']['PDF_DIR'])
IDENT_DIR = Path(config['PATHS']['IDENT_DIR'])
FAIL_DIR = Path(config['PATHS']['FAIL_DIR'])
LOG_DIR = Path(config['PATHS']['LOG_DIR'])
SENT_DIR = Path(config['PATHS']['SENT_DIR'])

if not PDF_DIR.is_dir():
    PDF_DIR.mkdir(parents=True)
if not IDENT_DIR.is_dir():
    IDENT_DIR.mkdir(parents=True)
if not LOG_DIR.is_dir():
    LOG_DIR.mkdir(parents=True)
if not SENT_DIR.is_dir():
    SENT_DIR.mkdir(parents=True)

IS_USR = config['ISUITE']['USERNAME']
IS_PWD = config['ISUITE']['PASSWORD']
IS_URL = config['ISUITE']['URL']

db_params = {
    "host" : config['ADRESSESDB']['HOST'],
    "dbname" : config['ADRESSESDB']['DBNAME'],
    "user" : config['ADRESSESDB']['USER'],
    "password" : config['ADRESSESDB']['password']
}

log_ident = setup_logger("ident", 'log/traces_ident.log')
log_envoi = setup_logger("envoi", 'log/traces_envoi.log')


#### Identification des documents ################################

address_db = call_addressdb(db_params)

if not address_db:
    log_ident.critical("Base de données adresses vide !")
    exit()

for pdf in PDF_DIR.iterdir():

    if not pdf.name.endswith(".pdf"):
        continue
    
    banner = "======={}{}".format(pdf.name, "="*(60-len(pdf.name)))
    log_ident.info(banner)
    print(banner)
    
    image = pdf_to_image(pdf)
    candidates = ocr_extract_and_order_words(image)
    
    winner, ranking = propose_winner(candidates, address_db)
    
    for i, rank in enumerate(ranking, start=1):
        log_ident.info(f"{i}, {rank}")
    
    if not winner:
        log_ident.warning(f"Aucune adresse ne correspond à {pdf.name}")
        shutil.move(pdf, PDF_DIR / "echec" / pdf.name)
        continue

    code, nom, origine = winner
    timestamp = datetime.now().strftime("%Y%m%d")
    log_ident.info(f"dossier propose : {nom}, ({code})")

    shutil.move(pdf, IDENT_DIR / f"{code}_{nom}_{origine}_{timestamp}.pdf")

#### Envoi paniere ################################

for pdf in IDENT_DIR.iterdir():

    print(f"Envoi paniere de {pdf.name}")

    if not pdf.suffix == ".pdf":
        continue

    parts = pdf.stem.split("_")
    if len(parts) == 4:
        code, nom, origine, stamp = parts

    isuite = ISuiteRequest(IS_URL, IS_USR, IS_PWD)
    isuite.select_dossier("FORMACLI")

    if not isuite.select:
        log_envoi.error(f"Echec connexion {isuite.response}")

    with open(pdf, "rb") as f:
        isuite.push_paniere(f, f"{origine}-{nom}-{stamp}.pdf")

    if isuite.depot:
        log_envoi.info(f"{origine}-{nom}-{stamp}.pdf")
        shutil.move(pdf, SENT_DIR / pdf.name)
    else:
        log_envoi.error(f"Echec envoi panière : {pdf.name}")
        log_envoi.error()
        shutil.move(pdf, FAIL_DIR / pdf.name)


