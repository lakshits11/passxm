import getpass
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
from utils.dbconfig import dbconfig
import utils.aesutil as aesutil
from rich import print as printc
from rich.console import Console

console = Console()


def computeMasterKey(mp, ds):
    password = mp.encode()
    salt = ds.encode()
    key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
    return key


# master password, device secret, sitename, siteurl, email, username
def addEntry(mp, ds, sitename, siteurl, email, username):
    # get the password
    pswrd = getpass.getpass("Enter the password: ")
    # encrypt the password using mp and ds
    mk = computeMasterKey(mp, ds)

    encrypted_password = aesutil.encrypt(key=mk, source=pswrd, keyType="bytes")

    # Add the entry to the database
    db = dbconfig()
    cursor = db.cursor()
    query = "INSERT INTO pm.entries (sitename, siteurl, email, username, password) VALUES (%s, %s, %s, %s, %s)"
    val = (sitename, siteurl, email, username, encrypted_password)
    cursor.execute(query, val)
    db.commit()
    printc("[green][+][/green] Entry added successfully")
