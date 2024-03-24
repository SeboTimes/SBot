from bs4 import BeautifulSoup as BS
from json import loads, dumps
from os.path import exists
from requests import get
from os import mkdir

for folder in ["Data/", "Sounds/"]:
    if not exists(folder):
        mkdir(folder)

for dataFile in ["Cryptos.json", "Items.json", "Users.json"]:
    if not exists(f"Data/{dataFile}"):
        with open(f"Data/{dataFile}", "w") as file:
            file.write("{}")

cashSymbol = "$"

def readData(which: str) -> dict:
    with open(f"Data/{which}.json", "r") as dataFile:
        return dict(loads(dataFile.read()))

def writeData(which: str, data: dict):
    with open(f"Data/{which}.json", "w") as dataFile:
        dataFile.write(dumps(data, indent=4, sort_keys=True))

def getPrices():
    _updatePrices()

    output = {}
    for inventory in ["Items", "Cryptos"]:
        items = readData(inventory)
        itemText = ""
        for item in items:
            itemText += f"\n`{item}: {items[item]}{cashSymbol}`"
        output[inventory] = itemText

    return f"Item prices:{output['Items']}\n\nCrypto prices:{output['Cryptos']}"

def _updatePrices():
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
