from datetime import datetime
from yt_dlp import YoutubeDL
from os.path import exists
from hashlib import sha256
from json import dumps

FFMPEG_OPTIONS = {
  "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
  "options": "-vn"
}

YTDL_OPTIONS = {
  "format": "bestaudio",
  "noplaylist": True,
  "quiet": True,
  "no_warnings": True
}

if not exists("Config.json"):
  with open("Config.json", "w") as cfgFile:
    cfg = {}
    cfg["Token"] = ""
    cfg["Activity.Type"] = 3
    cfg["Activity.Name"] = "you"
    cfg["AI.Host"] = "localhost:11434"
    cfg["AI.Model"] = "llama3.1"
    cfg["AI.System"] = ""
    cfg["Error.NoPerm"] = "You don't have the required permissions."
    cfg["Error.Queue"] = "Queue is empty."
    cfg["Error.Voice"] = "Bot is not in a voice channel."
    cfgFile.write(dumps(cfg, indent=2))

def sPrint(owner: str, msg: str):
  print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{owner}] {msg}")

def genHash(msg: str) -> str:
  return sha256(msg.encode()).hexdigest()

def fetchYtData(url: str) -> dict[str]:
  with YoutubeDL(YTDL_OPTIONS) as ytdl:
    return ytdl.extract_info(url, download=False)
