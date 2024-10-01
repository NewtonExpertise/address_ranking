
import pytesseract
from PIL import Image
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# custom_config = r"--psm 11 --dpi 300 -l fra -oem 1"
custom_config = r"--psm 11 --dpi 300 -l fra --oem 1"


def ocr_extract_and_order_words(image: Image) -> list:
    """
    OCR d'une image pour extraire le texte et la position de chaque
    mots dans l'espce de l'image (coord: x, y)
    Pour fonctionner il faut que tesseract soit déjà installé sur
    le poste : https://tesseract-ocr.github.io/tessdoc/Installation.html

    Parameters
    - image : PNG convertit au format PIL/Image

    Returns
    - liste des mots + coordonnées : (mot, x, y)

    """
    try:
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            lang="fra",
            config=custom_config)
    except:
        print("OCR couldn't open png")

    print("nombre de mots OCR : {}".format(len(data["text"])))

    wordlist = []

    for i, word in enumerate(data["text"]):
        if word == '':
            continue

        wordlist.append((
                data["text"][i],
                data["left"][i],
                data["top"][i]
        ))
        # Tri pour conserver l'ordre des mots tels qu'ils apparaissent sur le pdf
        wordlist = sorted(wordlist, key= lambda x : (x[2], x[1]))

    return wordlist

