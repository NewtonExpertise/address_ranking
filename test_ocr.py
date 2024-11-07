import sys
from pathlib import Path
from PIL import Image
from pdf_to_image import pdf_to_image
from ocerize import ocr_extract_and_order_words
from tkinter import Tk
from tkinter.filedialog import askopenfilename


Tk().withdraw()
pdf = askopenfilename()
if pdf:
    print(pdf)
else:
    sys.exit()

pdf_path = Path(pdf)
pdf_to_image(pdf_path)
png = r"temp.png"
img = Image.open(png)
words = ocr_extract_and_order_words(img)
[print(w) for w in words]