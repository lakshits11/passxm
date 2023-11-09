import hashlib
import getpass
import random
import string
import platform
import msvcrt
import sys
import time
import os

from datetime import datetime

import pyperclip

from utils.dbconfig import dbconfig
import utils.add
import utils.retrieve
import utils.generate
import utils.extract

from rich import print as printc
from rich.console import Console
from rich.markdown import Markdown

console = Console()
now = datetime.now()


def generateDeviceSecret(length=10):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_char():
    if platform.system() == "Windows":
        return msvcrt.getch().decode("utf-8")
    else:
        return msvcrt.getwch()


def config():
    # Create a Database
    db = dbconfig()
    cursor = db.cursor()

    printc("[green][+] Creating new config for you [/green]")

    try:
        cursor.execute("CREATE DATABASE pm")
    except Exception as e:
        printc("[red][!] An error occured while trying to create the database.")
        console.print_exception(show_locals=True)
        sys.exit(0)

    # Create tables
    query = "CREATE TABLE pm.secrets (masterkey_hash TEXT NOT NULL, device_secret TEXT NOT NULL)"
    res = cursor.execute(query)
    printc("[green][+][/green] Table 'secrets' created")

    query = "CREATE TABLE pm.entries (sitename TEXT NOT NULL, siteurl TEXT NOT NULL, email TEXT, username TEXT, password TEXT NOT NULL)"
    res = cursor.execute(query)
    printc("[green][+][/green] Table 'entries' created")

    mp = ""
    while True:
        mp = getpass.getpass("Choose a master password: ")
        if mp == getpass.getpass("Re-Type your master password: ") and mp != "":
            break
        printc(
            "[yellow][-] Please try again by entering a valid master password.[/yellow]"
        )

    # Hash the master password
    hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
    printc("[green][+][/green] Generated hash of Master Password")

    # Generate a device secret
    ds = generateDeviceSecret()

    # Add them to database
    query = "INSERT INTO pm.secrets (masterkey_hash, device_secret) VALUES (%s, %s)"
    val = (hashed_mp, ds)
    cursor.execute(query, val)
    db.commit()

    printc("[green][+][/green] Added to database")
    printc("[green][+] Configuration done! [/green]")
    db.close()


def inputAndValidateMasterPassword():
    typewriter_effect(
        "Please enter your master password: ", type_delay, delete_delay, endl=False
    )
    mp = getpass.getpass("")
    hashed_mp = hashlib.sha256(mp.encode()).hexdigest()

    db = dbconfig()
    cursor = db.cursor()
    query = "SELECT * FROM pm.secrets"
    cursor.execute(query)
    result = cursor.fetchall()[0]
    if hashed_mp != result[0]:
        printc("[red][!] WRONG! [/red]")
        return None
    db.close()
    return [mp, result[1]]


# How to check if secrets table in pm database exists?
def configNeeded():
    db = dbconfig()
    cursor = db.cursor()
    query = "SHOW DATABASES LIKE 'pm'"
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) == 1:
        q2 = "SHOW TABLES LIKE 'secrets'"
        cursor.execute(q2)
        result2 = cursor.fetchall()
        if len(result2) == 1:
            db.close()
            return False
    db.close()
    return True


PROGRAM_HEADING = """
# Welcome to PASSXM by Lakshit
"""

# Typing and Deleting speed in seconds
type_delay = 0.01
delete_delay = 0.01

dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


def typewriter_effect(sentence, type_delay, delete_delay, endl):
    for char in sentence:
        console.print(f"[bold]{char}[/bold]", style="#04de00", end="")
        time.sleep(type_delay)
    if endl:
        print()
    time.sleep(0.5)
    
def add_password(mp_ds):
    print()
    console.print(f"Adding new entry...")
    sitename = input("[optional] User Convinient Site Name: ")
    siteurl = input("[required] Site URL: ")
    while siteurl == "":
        siteurl = input("[required] Site URL: ")
    email = input("[optional] Email: ")
    username = input("[optional] Username: ")
    siteurl = utils.extract.extract_main_website(siteurl)
    utils.add.addEntry(mp_ds[0], mp_ds[1], sitename, siteurl, email, username)

def retrieve_password(mp_ds):
    console.print(f"Retrieving entry...")
    console.print(f"Enter sitename / siteurl / email / username to search for:")
    sitename = input("Site Name: ")
    siteurl = input("Site URL: ")
    email = input("Email: ")
    username = input("Username: ")
    search = {}
    # if sitename != "":
    search["sitename"] = sitename
    # if siteurl != "":
    if siteurl != "":
        siteurl = utils.extract.extract_main_website(siteurl)
    search["siteurl"] = siteurl
    if email != "":
        search["email"] = email
    if username != "":
        search["username"] = username
    utils.retrieve.retrieveEntries(
        mp_ds[0], mp_ds[1], search, decryptPassword=True
    )

def program():
    db = dbconfig()
    cursor = db.cursor()
    mp_ds = inputAndValidateMasterPassword()
    if mp_ds is None:
        return
    typewriter_effect("Logged in successfully.", type_delay, delete_delay, endl=True)
    typewriter_effect(dt_string, type_delay, delete_delay, endl=True)
    typewriter_effect(
        "Type 'l' to see the list of commands", type_delay, delete_delay, endl=True
    )
    print("")
    while True:
        console.print("[bold]$ [/bold]", style="#00cbcf", end="")
        cmd = get_char()
        if cmd == "l":
            print()
            console.print(f"[bold] [red]l[/red]ist of commands[/bold]", style="#04de00")
            console.print(f"[bold] [red]a[/red]dd new entry [/bold]", style="#04de00")
            console.print(f"[bold] [red]r[/red]etrieve entry [/bold]", style="#04de00")
            console.print(f"[bold] [red]s[/red]how all entries [/bold]", style="#04de00")
            console.print(f"[bold] [red]g[/red]enerate password [/bold]", style="#04de00")
            console.print(f"[bold] [red]e[/red]xit [/bold]", style="#04de00")

        elif cmd == "a":
            add_password(mp_ds)
        elif cmd == "r":
            retrieve_password(mp_ds)
        elif cmd == "s":
            print()
            console.print(f"Showing all entries...")
            utils.retrieve.retrieveEntries(mp_ds[0], mp_ds[1], {}, decryptPassword=False)
        elif cmd == "g":
            print()
            console.print(f"Generating password...")
            console.print(f"Enter length of the password to generate:")
            length = input("Length: ")
            password = utils.generate.generatePassword(int(length))
            pyperclip.copy(password)
            console.print(f"Password generated and copied to clipboard", style="#04de00")
            console.print(f"Do you also want to add this password? (y/n)", end="")
            addp = input()
            if addp=="y":
                add_password(mp_ds)
        elif cmd == "e":
            console.print(f"[bold] Bye! [/bold]", style="#04de00")
            break
        elif cmd == '\x03':
            printc("[yellow]Ctrl+C pressed. Exiting...[/yellow]")
            break
        else:
            printc("[red][!] Invalid command [/red]")


def main():
    if os.name == "nt":
        os.system("@cls")
    else:
        os.system("clear")
    console.print(Markdown(PROGRAM_HEADING), style="#04de00")
    program()


if __name__ == "__main__":
    main()
