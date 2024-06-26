from bs4 import BeautifulSoup as BS
from json import loads, dumps
from yt_dlp import YoutubeDL
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
    urlInfo = YoutubeDL().extract_info(url, False)
    data = readData("Songs")
    if url not in data:
        data[url] = urlInfo["title"]
        writeData("Songs", data)
    return data[url]

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
        cryptoText: str = cryptoSoup.find_all("span", {"class":"sc-d1ede7e3-0 fsQm base-text"})[0].text[1:].replace(",", "")
        cryptoData[crypto] = int(cryptoText.split(".")[0])
    
    writeData("Cryptos", cryptoData)
