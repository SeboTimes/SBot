from bs4 import BeautifulSoup as BS
from json import loads, dumps
from discord import Member
from requests import get

from Scripts.SFunctions import *

def readData(which: str) -> dict:
    with open(f"Data/{which}.json", "r") as dataFile:
        return loads(dataFile.read())

def writeData(which: str, data: dict):
    with open(f"Data/{which}.json", "w") as dataFile:
        dataFile.write(dumps(data, indent=4, sort_keys=True))

def doMemberData(member: Member):
    data = readData("Users")

    if member.bot:
        return
    
    print("Database", f"Refreshing '{member.name}'")

    if member.name not in data:
        data[member.name] = {
            "cash": 100,
            "cryptos": {}
        }

    cryptos = readData("Cryptos")
    for crypto in cryptos:
        if crypto not in data[member.name]["cryptos"]:
            data[member.name]["cryptos"][crypto] = 0

    for crypto in list(data[member.name]["cryptos"]):
        if crypto not in cryptos:
            data[member.name]["cryptos"].pop(crypto)

    writeData("Users", data)

def fetchYtData(url: str) -> str:
    songResp = get(url)
    songSoup = BS(songResp.text, "html.parser")
    songText = songSoup.find_all("meta", {"property": "og:video:tag"})
    return f"{songText[-2]["content"]} - {songText[0]["content"]}"

def updatePrices():
    cryptoData = {}

    cryptos = [
        "Bitcoin",
        "Ethereum",
        "BNB",
        "Solana",
        "Chainlink",
        "Bitcoin Cash",
        "Litecoin"
    ]

    for crypto in cryptos:
        cryptoResp = get(f"https://coinmarketcap.com/currencies/{crypto.replace(' ', '-')}/")
        cryptoSoup = BS(cryptoResp.text, "html.parser")
        cryptoText: str = cryptoSoup.find_all("span", {"class":"sc-f70bb44c-0 jxpCgO base-text"})[0].text[1:].replace(",", "")
        cryptoData[crypto] = int(cryptoText.split(".")[0])
    
    writeData("Cryptos", cryptoData)
