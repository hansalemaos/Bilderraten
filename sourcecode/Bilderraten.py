import pathlib
import requests
from maximize_console import *
import bs4
from requests.utils import quote
import re
from screen_ocr._winrt import WinRtBackend
from PIL import Image, ImageEnhance
from tkinter.filedialog import askopenfilename
from tkinter import Tk
from random import shuffle
import kthread
from time import time, sleep
from add_color_print_reg import *
import shutil

drucker = Farbprinter()
specialkeysde = [
    ["German special character:", "Use:"],
    ["ä", "a:"],
    ["ö", "o:"],
    ["ü", "u:"],
    ["Ä", "A:"],
    ["Ö", "O:"],
    ["Ü", "U:"],
    ["ß", "sz"],
]
specialkeyspt = [
    ["Portuguese special character:", "Use:"],
    ["á", "a'"],
    ["â", "a!"],
    ["ã", "a@"],
    ["à", 'a"'],
    ["c!", "ç"],
    ["é", "e'"],
    ["ê", "e!"],
    ["í", "i'"],
    ["ó", "o'"],
    ["ô", "o!"],
    ["õ", "o@"],
    ["ú", "u'"],
    ["Á", "A'"],
    ["Â", "A!"],
    ["Ã", "A@"],
    ["À", 'A"'],
    ["C!", "Ç"],
    ["É", "E'"],
    ["Ê", "E!"],
    ["Í", "I'"],
    ["Ó", "O'"],
    ["Ô", "O!"],
    ["Õ", "O@"],
    ["Ú", "U'"],
]
allespecialkeys = specialkeysde[1:] + specialkeyspt[1:]


def datei_auswaehlen(
    message="Please choose TXT file with vocabulary (one word each line)",
    debug=True,
    readfile=True,
):
    content = ""
    drucker.p.brightyellow.black.italic(message)

    Tk().withdraw()
    filetypes = [("text files", "*.txt")]
    datei = askopenfilename(title=message, filetypes=filetypes)
    pathlibpfad = pathlib.Path(datei)
    if debug is True:
        drucker.p.brightyellow.black.italic(pathlibpfad)

    if readfile is True:
        try:
            content = pathlibpfad.read_text(encoding="utf-8")
        except:
            content = pathlibpfad.read_bytes()
    return pathlibpfad, content


def vokabelliste_einlesen():
    pfad, woerter = datei_auswaehlen(
        message="Please choose TXT file with vocabulary (one word each line)",
        debug=True,
        readfile=True,
    )
    woerter = woerter.splitlines()
    woerter = [str(w).strip() for w in woerter]
    escapedwords = [[w, quote(w, safe="")] for w in woerter]
    escapedwords = [
        [
            w[0],
            w[1],
            f"https://www.google.com/search?q={w[1]}&tbm=isch&hl=en&tbs=itp:clipart",
        ]
        for w in escapedwords
    ]
    return escapedwords


def get_htmllinks_of_wort(escapedwords):
    if not os.path.exists("tempbilder"):
        os.makedirs("tempbilder")
    fertigebilder = []
    htmlcode = requests.get(escapedwords[-1])
    suppe = bs4.BeautifulSoup(htmlcode.text, "html.parser")
    allebilder = suppe.findAll("img")
    for endi, bi in enumerate(allebilder):
        try:
            fertigebilder.append(
                [
                    f"tempbilder/{str(endi).zfill(7)}.png",
                    re.findall(r'src="(https://[^"]+)"', str(bi))[0],
                ]
            )
        except:
            continue
    return fertigebilder.copy()


def bildspeichern(bildname):
    with open(bildname[0], "wb") as f:
        f.write(requests.get(bildname[1]).content)
    gespeichertebilder.append(bildname[0])


def textrausschmeissen(gespeichertebilder):
    bilderohnetext = []
    for gesp in gespeichertebilder:
        bildfuerocr = Image.open(gesp).convert("L")
        bildfuerocr = bildfuerocr.convert("RGBA")
        bildfuerocr = ImageEnhance.Contrast(bildfuerocr).enhance(2)
        ocrbild = ocrscanner.run_ocr(bildfuerocr)
        for alle in ocrbild.lines:
            woerter = alle.words
            if any(woerter):
                bilderohnetext.append(gesp)
    brauchebarebilder = list(set(gespeichertebilder).difference(set(bilderohnetext)))
    return brauchebarebilder


def bilderstellen(brauchebarebilder):
    xeinfuegen = 0
    yeinfuegen = 0
    imggross = Image.new("RGBA", size=(1000, 2000), color=(255, 255, 255, 255))
    for indi, brauchbild in enumerate(brauchebarebilder):
        if yeinfuegen > 2000:
            break
        if indi % 2 == 0:
            continue
        img1 = Image.open(brauchbild).convert("RGBA")
        bildgroesse = img1.size
        faktor = 499 / bildgroesse[0]
        img1 = img1.resize((499, int(bildgroesse[1] * faktor)))
        img1 = ImageEnhance.Contrast(img1).enhance(3)
        imggross.paste(img1, (xeinfuegen, yeinfuegen))
        xeinfuegen = 499 + xeinfuegen
        if xeinfuegen == 998:
            yeinfuegen = yeinfuegen + 499
            xeinfuegen = 0
    imggross.save("tempbilder/endbild.png")


def delete_old_images():
    for bild in gespeichertebilder:
        os.remove(bild)
    os.remove("tempbilder/endbild.png")


def flattenlist(iterable):
    def iter_flatten(iterable):
        it = iter(iterable)
        for e in it:
            if isinstance(e, (list, tuple)):
                for f in iter_flatten(e):
                    yield f
            else:
                yield e

    a = [i for i in iter_flatten(iterable)]
    return a


def checken_if_tempbilder_noch_da():
    target_dir = "tempbilder"
    try:
        with os.scandir(target_dir) as entries:
            for entry in entries:
                if entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry.path)
                else:
                    os.remove(entry.path)
    except:
        pass


print(1000 * "\n")

maximize_console(lines=30000)
checken_if_tempbilder_noch_da()
add_color_print_to_regedit()
colorfunctionslogo = [drucker.f.black.red.normal, drucker.f.black.brightyellow.normal]
drucker.p_ascii_front_on_flag_with_border(
    text="Bilderraten",
    colorfunctions=colorfunctionslogo,
    bordercolorfunction=drucker.f.brightgreen.black.italic,
    font="slant",
    width=1000,
    offset_from_left_side=5,
    offset_from_text=15,
)
colorfunctionspage = [
    drucker.f.black.brightwhite.normal,
    drucker.f.black.brightgreen.normal,
]
drucker.p_ascii_front_on_flag_with_border(
    text="www . queroestudaralemao . com . br",
    colorfunctions=colorfunctionspage,
    bordercolorfunction=drucker.f.brightgreen.black.negative,
    font="slant",
    width=1000,
    offset_from_left_side=1,
    offset_from_text=1,
)

updates_quero_estudar_alemao()
allewoerter = vokabelliste_einlesen()
shuffle(allewoerter)
allebilderlinks = []
htmllinks = []
ocrscanner = WinRtBackend()
picturesize = 60
colorfunctions = [drucker.f.black.red.normal, drucker.f.black.white.normal]
gesamtpunktzahl = 0
for escapedwords in allewoerter:
    htmllinks = get_htmllinks_of_wort(escapedwords)
    gespeichertebilder = []
    allethreads = [
        kthread.KThread(target=bildspeichern, args=[xxx], name=xxx[0])
        for xxx in htmllinks
    ]
    allethreads2 = [k.start() for k in allethreads]
    nochamleben = [k.is_alive() for k in allethreads]
    nochamleben = [istda for istda in nochamleben if istda is True]
    t_end = time() + 10
    while any(nochamleben):
        if time() > t_end:
            for k in allethreads:
                try:
                    k.terminate()
                except:
                    continue
        sleep(0.1)
        nochamleben = [k.is_alive() for k in allethreads]
        nochamleben = [istda for istda in nochamleben if istda is True]

    brauchebarebilder = textrausschmeissen(gespeichertebilder)
    shuffle(brauchebarebilder)
    bilderstellen(brauchebarebilder)
    bildascii = drucker.p_picture_to_ascii_art(
        "tempbilder/endbild.png",
        letter_for_ascii_art="█",
        rgb8_16_256=256,
        desired_width=60,
    )
    print(bildascii)
    drucker.p_pandas_list_dict(specialkeysde, listtranspose=True)
    drucker.p_pandas_list_dict(specialkeyspt, listtranspose=True)
    langegesuchteswort = len(escapedwords[0]) * "_"

    drucker.p_ascii_front_on_flag_with_border(
        text=langegesuchteswort,
        colorfunctions=colorfunctions,
        bordercolorfunction=drucker.f.brightmagenta.brightcyan.negative,
        font="roman",
        width=1000,
        offset_from_left_side=5,
        offset_from_text=15,
    )

    antwort = str(
        input(
            drucker.f.brightyellow.black.bold(
                "\n                    What word are we looking for?            \n"
            )
        )
    ).strip()
    for key in allespecialkeys:
        antwort = antwort.replace(key[1], key[0])
    tippsgeben = True
    if antwort == escapedwords[0]:
        gesamtpunktzahl = gesamtpunktzahl + 1
        tippsgeben = False
    while tippsgeben is True:
        hint = (
            drucker.f.black.brightwhite.bold("\nIs it too hard? Do you need any tips? ")
            + drucker.f.black.yellow.bold("\nType ")
            + drucker.f.black.brightyellow.bold("?")
            + drucker.f.black.yellow.bold(" to see the next letter\n")
            + drucker.f.black.brightred.italic(
                "(Attention: special characters are usually not shown!)\n"
            )
        )
        print(hint)
        antwort = str(
            input(
                drucker.f.brightyellow.black.bold(
                    "\n                    What word are we looking for?            \n"
                )
            )
        ).strip()

        if antwort == "?":
            neueswortdrucken = []
            strichwort = flattenlist(langegesuchteswort)
            richtigeswort = flattenlist(escapedwords[0])
            for strichw, richtigesw in zip(strichwort, richtigeswort):
                if strichw == "_":
                    neueswortdrucken.append(richtigesw)
                    break
                if strichw != "_":
                    neueswortdrucken.append(richtigesw)
            neueswortdrucken.append((len(strichwort) - len(neueswortdrucken)) * "_")
            langegesuchteswort = "".join(neueswortdrucken)

            drucker.p_ascii_front_on_flag_with_border(
                text=langegesuchteswort,
                colorfunctions=colorfunctions,
                bordercolorfunction=drucker.f.brightmagenta.brightcyan.negative,
                font="roman",
                width=1000,
                offset_from_left_side=5,
                offset_from_text=15,
            )
            if "_" not in langegesuchteswort:
                break
        if antwort == escapedwords[0]:
            gesamtpunktzahl = gesamtpunktzahl + 1
            break
    punkzahldrucken = (
        drucker.f.green.brightwhite.bold(f"\n\nYour points: {gesamtpunktzahl} ")
        + drucker.f.black.brightwhite.bold(" of ")
        + drucker.f.brightwhite.green.bold(f"{len(allewoerter)} points  \n\n")
    )
    print(punkzahldrucken)
    delete_old_images()
