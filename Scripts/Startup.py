from os.path import exists
from os import mkdir

for folder in ["Data/", "Sounds/"]:
    if not exists(folder):
        mkdir(folder)

for dataFile in ["Cryptos.json", "Users.json"]:
    if not exists(f"Data/{dataFile}"):
        with open(f"Data/{dataFile}", "w") as file:
            file.write("{}")
