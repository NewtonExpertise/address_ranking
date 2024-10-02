
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
    Download : https://objects.githubusercontent.com/github-production-release-asset-2e65be/47605084/9c763d61-6460-41e1-945c-eb0e6ef09a95?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=releaseassetproduction%2F20241001%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20241001T165826Z&X-Amz-Expires=300&X-Amz-Signature=aad170b026fc8986bb8077137bd19f794e7360da1ade550adfe914a6c8b6e827&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3Dtesseract-ocr-w64-setup-5.4.0.20240606.exe&response-content-type=application%2Foctet-stream

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

