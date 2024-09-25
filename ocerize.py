
import pytesseract
from PIL import Image
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# custom_config = r"--psm 11 --dpi 300 -l fra -oem 1"
custom_config = r"--psm 11 --dpi 300 -l fra --oem 1"

def ocr_extract_words(image: Image) -> list:
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

        print(data["text"][i], data["width"][i])
        wordlist.append((
                data["text"][i],
                data["left"][i]+data["width"][i]/2,
                data["top"][i]+data["height"][i]/2
        ))

    return wordlist

def ocr_extract_short_words(image: Image) -> list:
    try:
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            lang="fra",
            config=custom_config)
    except:
        print("OCR couldn't open png")

    print("nombre de mots OCR : {}".format(len(data["text"])))

    # print(data["text"])

    wordlist = []

    for i, word in enumerate(data["text"]):
        if word == '':
            continue

        # if 0 < len(word) < 8:
        print(data["text"][i], data["width"][i])
        if data["width"][i] < 100 :
            wordlist.append((
                    data["text"][i],
                    data["left"][i]+data["width"][i]/2,
                    data["top"][i]+data["height"][i]/2
            ))
        else:
            middle = len(word) // 2
            w1 = word[:middle]
            w2 = word[middle:]
            x1 = data["left"][i]+data["width"][i]/4
            y1 = data["top"][i]+data["height"][i]/2
            x2 = data["left"][i]+data["width"][i]*(3/4)
            y2 = data["top"][i]+data["height"][i]/2
            wordlist.append((w1, x1, y1))
            wordlist.append((w2, x2, y2))

    return wordlist

def make_segment(word, x, y, w, h):
    # result = word, (int(x), int(y + (h/2))), (int(x + w), int(y + (h/2))) 
    result = word, (x, y + h/2), (x + w, y + h/2)
    return result

def ocr_extract_words_segm(image: Image) -> list:
    try:
        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            lang="fra",
            config=custom_config)
    except:
        print("OCR couldn't open png")

    print("nombre de mots OCR : {}".format(len(data["text"])))

    # print(data["text"])

    wordlist = []

    for i, word in enumerate(data["text"]):
        if len(word) > 0:
            segment = make_segment(
                data["text"][i],
                data["left"][i],
                data["top"][i],
                data["width"][i],
                data["height"][i]
            )
            wordlist.append(segment)

    return wordlist

def ocr_extract_and_order_words(image: Image) -> list:
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

        wordlist = sorted(wordlist, key= lambda x : (x[2], x[1]))

    return wordlist



if __name__ == "__main__":
    chemin = r"V:\Informatique\Dev\ancv_matrix\temp_bdo.png"
    # chemin = r"V:\Informatique\Dev\ancv_matrix\temp_1.png"
    img = Image.open(chemin)
    # [print(x) for x in ocr_extract_words_segm(img)]
    [print(x) for x in ocr_extract_and_order_words(img)]
