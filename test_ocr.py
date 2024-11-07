import sys
import math
from pathlib import Path
from PIL import Image
from pdf_to_image import pdf_to_image
from ocerize import ocr_extract_and_order_words
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from call_addressdb import call_addressdb
import configparser

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

config = configparser.ConfigParser()
config.read("config.ini", encoding='ansi')
db_params = {
    "host" :   config['ADRESSESDB']['HOST'],
    "dbname" : config['ADRESSESDB']['DBNAME'],
    "user" :   config['ADRESSESDB']['USER'],
    "password" : config['ADRESSESDB']['password']
}

Tk().withdraw()
pdf = askopenfilename()
if pdf:
    print(pdf)
else:
    sys.exit()

pdf_path = Path(pdf)
pdf_to_image(pdf_path, keep_png=True)
png = r"temp.png"
img = Image.open(png)
candidates = ocr_extract_and_order_words(img)

for word in candidates:
    print(word)

address_db = call_addressdb(db_params)

winner, ranking = propose_winner(candidates, address_db)
print(winner)
for item in ranking:
    print("---", item)
