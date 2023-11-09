import hashlib
import getpass
import random
import string
import sys
from utils.dbconfig import dbconfig

from rich import print as printc
from rich.console import Console

console = Console()


def generateDeviceSecret(length=10):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

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

if __name__ == "__main__":
    config()