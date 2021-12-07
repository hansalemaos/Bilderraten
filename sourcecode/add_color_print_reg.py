from json import loads as jsonloads
from os import name as osname
from sys import exit as sysexit
from textwrap import TextWrapper
from random import choice
from requests import get as requestsget
from farbprinter.farbprinter import Farbprinter

windowsrechner = osname == "nt"
from winregistry import WinRegistry
from winreg import HKEY_CURRENT_USER, KEY_READ, REG_DWORD

linebreakx = 50
wrapper = TextWrapper(width=linebreakx)
drucker = Farbprinter()
jsonqueroestudaralemao = "https://www.queroestudaralemao.com.br/wp-content/uploads/updateinformatioen/update.json"
logo_auswahl = auswahlliste = [
    drucker.f.brightred.black.bold,
    drucker.f.black.brightred.bold,
    drucker.f.yellow.black.bold,
    drucker.f.brightyellow.black.bold,
]
REGEDITPATH = r"HKEY_CURRENT_USER\Console"
regedit_success = "I think, it has worked out! Let's start"
virtualterminalregedit = "VirtualTerminalLevel"
able_to_see_col_text = "Everything is configured right! You should be able to see colored text! Please restart the app if you can't see colored text"
regedit_is_zero = "HKEY_CURRENT_USER\Console\VirtualTerminalLevel is set to 0! I will try to change it to 1 so that you can read colored text!"
regeditfail = """I was unable to change the Registry!\n Let\'s try it anyway!\n If you can\'t read the text in the terminal, add this to your Windows Registry:\n\n[HKEY_CURRENT_USER\Console]\n
"VirtualTerminalLevel"=dword:00000001"""
try_to_create_key = "HKEY_CURRENT_USER\Console\VirtualTerminalLevel not found! I will try to create it so that you can see colored text"


def add_color_print_to_regedit():
    if windowsrechner:
        try:
            with WinRegistry() as client:
                try:

                    regedit_entry = client.read_entry(
                        REGEDITPATH, virtualterminalregedit
                    )
                    if int(regedit_entry.value) == 1:
                        print(drucker.f.black.green.negative(able_to_see_col_text))
                        return True
                    if int(regedit_entry.value) == 0:
                        print(drucker.f.black.brightyellow.negative(regedit_is_zero))
                        try:
                            client.write_entry(
                                REGEDITPATH,
                                virtualterminalregedit,
                                value=1,
                                reg_type=REG_DWORD,
                            )
                            print(drucker.f.black.green.negative(regedit_success))
                        except:
                            print(drucker.f.black.brightred.negative(regeditfail))
                            return False
                except:
                    print(drucker.f.black.brightyellow.negative(try_to_create_key))
                    try:
                        client.write_entry(
                            REGEDITPATH,
                            "VirtualTerminalLevel",
                            value=1,
                            reg_type=REG_DWORD,
                        )
                        print(drucker.f.black.green.negative(regedit_success))

                        return True
                    except:
                        print(drucker.f.black.brightred.negative(regeditfail))
                        return False
        except:
            print(
                drucker.f.black.brightred.negative(
                    "Error checking if VirtualTerminalLevel is set to 1"
                )
            )


def updates_quero_estudar_alemao():
    choice(auswahlliste)("made by queroestudaralemao.com.br")
    print(
        drucker.f.black.brightblue.bold(
            "\n         Updates from http://www.queroestudaralemao.com.br :\n\n"
        )
    )

    jsoninhalt = requestsget(jsonqueroestudaralemao)
    j = jsonloads(jsoninhalt.text)

    for key, value in j.items():
        neuigkeitendatum = drucker.f.cyan.brightwhite.italic(
            f"""         {key} - News from    """.ljust(20).rjust(20)
        )
        print(neuigkeitendatum, end=" ")
        print(
            drucker.f.black.brightwhite.negative(f'       {value["autor"]}:        '),
            end=" ",
        )
        print(
            drucker.f.brightwhite.blue.negative(f'       {value["datum"]}:        '),
            end=" ",
        )
        neuigkeitenwrap = wrapper.wrap(text=value["neuigkeiten"])
        print("\n")
        for satz in neuigkeitenwrap:
            print(drucker.f.black.brightyellow.bold("     "), end="")
            ausfuellen = (70 - len(satz)) * " "
            print(
                drucker.f.black.brightyellow.bold(f"   {satz}   {ausfuellen}"), end="\n"
            )
        if value["online"] == "0":
            print(value["nachricht"])
            sysexit()
        print("\n")
