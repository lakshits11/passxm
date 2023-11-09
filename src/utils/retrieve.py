import pyperclip
from utils.dbconfig import dbconfig
from rich import print as printc
from rich.console import Console
from rich.table import Table
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
import utils.aesutil as aesutil

console = Console()


def computeMasterKey(mp, ds):
    password = mp.encode()
    salt = ds.encode()
    key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)
    return key


# master password, device secret, string to search(maybe empty or partial)
# If user actually want to see the password, he will specify a '-p' flag in commandline and decryptPassword will be True
def retrieveEntries(mp, ds, search, decryptPassword=False):
    db = dbconfig()
    cursor = db.cursor()
    reqSitename, reqSiteurl = "", ""
    if len(search)!= 0:
        reqSitename = search["sitename"]
        reqSiteurl = search["siteurl"]

    if len(search) == 0:
        query = "SELECT * FROM pm.entries"
    elif reqSitename != "" and reqSiteurl == "":
        query = "SELECT * FROM pm.entries WHERE sitename LIKE '%{reqSitename}%'".format(
            reqSitename=reqSitename
        )
    elif reqSiteurl == "" and reqSitename != "":
        query = "SELECT * FROM pm.entries WHERE siteurl LIKE '%{reqSiteurl}%'".format(
            reqSiteurl=reqSiteurl
        )
    else:
        query = "SELECT * FROM pm.entries WHERE (sitename LIKE '%{reqSitename}%' OR siteurl LIKE '%{reqSiteurl}%') AND (sitename != '' AND siteurl != '')"

    cursor.execute(query.format(reqSitename=reqSitename, reqSiteurl=reqSiteurl))
    results = cursor.fetchall()

    if len(results) == 0:
        printc("[yellow][-][/yellow] No results found for the given search query :(")
        return

    table = Table(title="Results")
    table.add_column("ID")
    table.add_column("Site Name")
    table.add_column("Site URL")
    table.add_column("Email")
    table.add_column("Username")
    table.add_column("Password")
    if decryptPassword != True:
        sn = 1
        for row in results:
            table.add_row(str(sn), row[0], row[1], row[2], row[3], "*#*#*#*#*#*#*")
            sn += 1
        console.print(table)
        return

    if decryptPassword == True:
        mk = computeMasterKey(mp, ds)
        for i in range(len(results)):
            # decrypted_password = aesutil.decrypt(
            #     key=mk, source=results[i][4], keyType="bytes"
            # )
            table.add_row(
                str(i + 1),
                results[i][0],
                results[i][1],
                results[i][2],
                results[i][3],
                # decrypted_password.decode(encoding="utf-8"),  # change this line to a "********" if you don't want to show the password
                "********",  # change this line to a "********" if you don't want to show the password
            )
        console.print(table)

        # now ask the user to enter number of result to copy to clipboard
        while True:
            printc(
                "[yellow][!][/yellow] Enter the number of result to copy to clipboard: "
            )
            inp = int(input())
            if inp > 0 and inp <= len(results):
                tmp = aesutil.decrypt(
                    key=mk, source=results[i - 1][4], keyType="bytes"
                ).decode(encoding="utf-8")
                pyperclip.copy(tmp)
                printc("[green][+][/green] Desired Password copied to clipboard 👍")
                break
            else:
                printc("[red][-][/red] Invalid input")

    db.close()
