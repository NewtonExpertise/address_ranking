import math
import logging
import configparser
import shutil
from datetime import datetime
from pathlib import Path
from pdf_to_image import pdf_to_image
from ocerize import ocr_extract_and_order_words


logging.basicConfig(
    filename= f"./log/traces.log",
    filemode="w",
    format='%(asctime)s-%(module)s \t %(levelname)s - %(message)s',
    level="INFO",
    encoding="cp1252"
)

config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')
PDF_DIR = Path(config['PATHS']['PDF_DIR'])
ADR_DIR = Path(config['PATHS']['ADR_DIR'])
LOG_DIR = Path(config['PATHS']['LOG_DIR'])

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

def calc_match_ratio(candidates: list, trial: list) -> float:
    """
    Recherche le nombre de mots communs entre les deux listes
    Vérifie si :
    - chaque mot est présent
    - si ses coordonnées sont à une distance < à 20 pixels
    Si OK, renvoi un ratio de correspondance

    Parameters 
    - candidates : mots à évaluer
    - trial: mots de référence

    Return
    - float
    """
    ratio = 0.
    matches = []
    for can_w, can_x, can_y in candidates:
        for tri_w, tri_x, tri_y in trial:
            if can_w == tri_w:
                distance = calc_distance((can_x, can_y), (tri_x, tri_y))
                if distance <= 50:
                    print("\t", can_w, tri_w, distance)
                    matches.append((can_w, can_x, can_y))
    if matches:
        ratio = len(matches) / len(trial)
    return ratio

def rename_winner(pdf: Path, nameparts: list) -> bool:
    """
    Renomme le fichier en fonction des élements fournis dans nameparts
    """
    dossier, code, vendor = nameparts
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{vendor} {code} {timestamp}.pdf"
    newpath = pdf.parent / filename
    try:
        shutil.move(pdf, newpath)
        success = True
    except:
        logging.error("Impossible de renommer le fichier")
        filename = ""
    return filename

#####################################################################

address_db = build_address_book(ADR_DIR)

for pdf in PDF_DIR.iterdir():
    print(f"============{pdf.name}==================")

    if not pdf.name.endswith(".pdf"):
        continue

    ranking = []
    
    image = pdf_to_image(pdf)
    candidates = ocr_extract_and_order_words(image)
    
    for address in address_db:
        trial = address[1]
        ratio = calc_match_ratio(candidates, trial)
        ranking.append((ratio, address[0]))

    
    for i, (ratio, name) in enumerate(sorted(ranking, reverse=True), start=1):
        print(f"{i}. {name} ({ratio})")
    
    for ratio, name in ranking:
        if ratio >= 1.:
            winner = sorted(ranking, reverse=True)[0]
            dossier, code, vendor = name.split("_")
            break
    x = rename_winner(pdf, [dossier, code, vendor])
    if x:
        logging.info("x")


    print("#### RANKING ####")



