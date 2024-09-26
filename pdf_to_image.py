import subprocess
from tempfile import TemporaryDirectory
from PIL import Image
from pathlib import Path


def pdf_to_image(pdf_path: Path, keep_png: bool = False) -> Image:
    """
    Convertit un PDF au format PNG.
    N'est conservé que le tiers supérieur de l'image, suffisant pour identifier l'origine.
    Nécessite la présence de l'exécutable PDFTOPNG.EXE dans le même dossier.
    Va créer un fichier temporaire avant le redimmensionnement.
    
    parameters :
    - pdf_path : chemin du fichier pdf au format pathlib.Path
    - keep_png : supprimer ou non le fichier PNG créé

    returns :
    - Image : png au format pillow Image

    """
    result = None
    pdftopng = r"pdftopng.exe"
    temp = TemporaryDirectory()
    png_temp = Path(temp.name) / "temp_png"
    # params = [pdftopng, "-f",  "1",  "-l" , "1", "-r", "300", pdf_path, png_temp]
    params = [pdftopng, "-f",  "1",  "-l" , "1", "-gray", "-r", "300", pdf_path, png_temp]
    exec = subprocess.run(params)
    
    if not exec.returncode == 0:
        print("PNG conversion failed", "\n", result)
        return result

    png_path = str(png_temp) + "-000001.png"
    
    try:
        img = Image.open(png_path)
    except IOError as e:
        print(e)
        return result
    
    width, height = img.size
    img = img.crop((0, 0, width, height/3))
    size = (1500, 750)
    # size = (1000, 500)
    img = img.resize(size)

    # cleaning temporary png file
    temp.cleanup()
        
    result = img

    if keep_png:
        img.save("temp.png")

    return result


if __name__ == "__main__":

    # # pdf = r"\\kiev\Qappli\Quadra\DATABASE\cpta\DC\000354\Images\000354_1475.pdf"
    # pdf1 = Path(r"C:\temp\ML DATA SET\pdf\PLUXEE\PLUXEE DBLG (3).pdf")
    # pdf1 = Path(r"V:\Informatique\Dev\doc_pipe\pdf_plaga_pluxee\COM PLUXEE-2024-01-12--19,07 E.pdf")
    pdf1 = Path(r"C:\temp\ML DATA SET\pdf\Misc\small\EDENRED ALKARIC (6).pdf")
    img = pdf_to_image(pdf1, keep_png=True)
    # img.save("test.png")
    # pdf = r"V:\Informatique\Dev\doc_pipe\pdf_plaga_pluxee\COM PLUXEE-2024-01-12--19,07 E.pdf"
    # ref = r"V:\Informatique\Dev\doc_pipe\references\pluxee\_facture.png"