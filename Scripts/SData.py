from json import loads, dumps
from yt_dlp import YoutubeDL
from discord import Member

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
    
    sPrint("Database", f"Refreshing '{member.name}'")

    if member.name not in data:
        data[member.name] = {
            "cash": 100,
        }

    writeData("Users", data)

def fetchYtData(url: str) -> str:
    data = readData("Songs")
    if not url in data:
        urlInfo = YoutubeDL().extract_info(url, False)
        data[url] = urlInfo["title"]
        writeData("Songs", data)
    return data[url]
