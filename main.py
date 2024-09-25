import math
from pathlib import Path
from pdf_to_image import pdf_to_image
from ocerize import ocr_extract_and_order_words


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

def run(pdf_folder: Path, address_folder: Path) -> None:

    address_db = build_address_book(address_folder)

    for pdf in pdf_folder.iterdir():

        if not pdf.name.endswith(".pdf"):
            continue

        ranking = []
        
        image = pdf_to_image(pdf)
        candidates = ocr_extract_and_order_words(image)
        
        for address in address_db:
            trial = address[1]
            ratio = calc_match_ratio(candidates, trial)
            ranking.append((ratio, address[0]))

        print("#### RANKING ####")
        for i, (ratio, name) in enumerate(sorted(ranking, reverse=True), start=1):
            print(f"{i}. {name} ({ratio})")

if __name__ == "__main__":

    pdf = Path(r"V:\Informatique\Dev\address_ranking\pdf")
    adresses = Path(r"V:\Informatique\Dev\address_ranking\adresses")

    run(pdf, adresses)