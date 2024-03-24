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
        return None
    
    print("Database", f"Refreshing '{member.name}'")

    if member.name not in data:
        data[member.name] = {
            "cash": 100,
            "items": {},
            "cryptos": {}
        }

    for inventory in ["Items", "Cryptos"]:
        items = readData(inventory)

        for item in items:
            if item not in data[member.name][inventory.lower()]:
                data[member.name][inventory.lower()][item] = 0

        for item in list(data[member.name][inventory.lower()]):
            if item not in items:
                data[member.name][inventory.lower()].pop(item)

    writeData("Users", data)

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
