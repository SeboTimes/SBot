from datetime import datetime
from hashlib import sha256
from os.path import exists
from os import system

from rich import print as _print
from discord.ext import commands
from mutagen.mp3 import MP3
from asyncio import sleep
from gtts import gTTS
import discord as dc

from Data import *

def print(owner: str, msg: str):
    _print(f"[bright_black]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bright_black] [blue bold]{owner}[/blue bold] {msg}")

def doUserData(user: dc.User):
    print("Database", f"Refreshing '{user.name}'")
    data = readData("Users")

    if str(user.id) not in data:
        data[str(user.id)] = {
            "name": "",
            "cash": 100,
            "xp": 0,
            "items": {},
            "cryptos": {}
        }

    for inventory in ["Items", "Cryptos"]:
        items = readData(inventory)

        for item in items:
            if item not in data[str(user.id)][inventory.lower()]:
                data[str(user.id)][inventory.lower()][item] = 0

        for item in list(data[str(user.id)][inventory.lower()]):
            if item not in items:
                data[str(user.id)][inventory.lower()].pop(item)

    data[str(user.id)]["name"] = user.name
    writeData("Users", data)

def genHash(msg: str) -> str:
    return sha256(msg.encode()).hexdigest()

bot = commands.Bot(intents=dc.Intents.all())

infoMsg: dc.Message = None

async def response(ctx: commands.Context, msg: str):
    await ctx.respond(embed=dc.Embed(description=msg))

async def playSound(member: dc.Member, path: str):
    voice: dc.VoiceClient = member.guild.voice_client
    if voice != None:
        await voice.disconnect()

    voiceChannel: dc.VoiceChannel = member.voice.channel
    if voiceChannel != None:
        await voiceChannel.connect()

        voice: dc.VoiceClient = member.guild.voice_client
        if not voice.is_playing():
            voice.play(dc.FFmpegPCMAudio(path))
            await sleep(MP3(path).info.length)
            await voice.disconnect()

@bot.event
async def on_ready():
    global infoMsg

    await bot.change_presence(activity=dc.Activity(type=dc.ActivityType.playing, name="with joe mama"))
    print("Main", f"Logged in as {bot.user} on {len(bot.guilds)} guild(s)!")

    print("Database", "Syncing users...")
    for guild in bot.guilds:
        async for member in guild.fetch_members():
            doUserData(member)
    print("Database", "Done.")

    print("App", "Syncing commands...")
    await bot.sync_commands(guild_ids=[guild.id for guild in bot.guilds])
    for cmd in bot.application_commands:
        print("App", f"Synced '{cmd.name}'")
    print("App", "Done.")

@bot.event
async def on_member_join(member: dc.Member):
    doUserData(member)

@bot.event
async def on_message(message: dc.Message):
    data = readData("Users")
    data[str(message.author.id)]["xp"] += 1
    writeData("Users", data)

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def ping(ctx: commands.Context):
    await response(ctx, f"Pong: {bot.latency}ms")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def wallet(ctx: commands.Context):
    data = readData("Users")
    await response(ctx, f"In your wallet are `{data[str(ctx.author.id)]['cash']}{cashSymbol}`.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def inventory(ctx: commands.Context):
    data = readData("Users")
    outputs = {}
    for inventory in ["items", "cryptos"]:
        itemText = ""
        for item in data[str(ctx.author.id)][inventory]:
            if data[str(ctx.author.id)][inventory][item] > 0:
                itemText += f"\n`{data[str(ctx.author.id)][inventory][item]}x {item}`"
        if len(itemText) > 0: outputs[inventory] = itemText
    
    msg = ""
    for output in outputs:
        msg += f"{output[0].upper()+output[1:]}: {outputs[output]}\n\n"

    if len(msg) > 0:
        await response(ctx, msg)
    else:
        await response(ctx, "Your inventory is empty.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
@dc.option("action", autocomplete=lambda: ["buy", "sell"])
@dc.option("item", autocomplete=lambda: [item for item in readData("Items")])
async def item(ctx: commands.Context, action: str, item: str, amout: int = 1):
    data = readData("Users")
    items = readData("Items")

    if action == "buy":
        if data[str(ctx.author.id)]["cash"] >= items[item] * amout:
            await response(ctx, f"You bought `{amout}x {item}` for `{items[item] * amout}{cashSymbol}`.")
            data[str(ctx.author.id)]["items"][item] += 1 * amout
            data[str(ctx.author.id)]["cash"] -= items[item] * amout
        else:
            await response(ctx, f"You don't have enough money.")
    elif action == "sell":
        if data[str(ctx.author.id)]["items"][item] >= amout:
            await response(ctx, f"You sold `{amout}x {item}` for `{items[item] * amout}{cashSymbol}`.")
            data[str(ctx.author.id)]["items"][item] -= amout
            data[str(ctx.author.id)]["cash"] += items[item] * amout
        else:
            await response(ctx, f"You don't have enough `{item}s`.")
    
    writeData("Users", data)

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
@dc.option("action", autocomplete=lambda: ["buy", "sell"])
@dc.option("crypto", autocomplete=lambda: [crypto for crypto in readData("Cryptos")])
async def crypto(ctx: commands.Context, action: str, crypto: str, amout: int = 1):
    data = readData("Users")
    items = readData("Cryptos")

    if action == "buy":
        if data[str(ctx.author.id)]["cash"] >= items[crypto] * amout:
            await response(ctx, f"You bought `{amout}x {crypto}` for `{items[crypto] * amout}{cashSymbol}`.")
            data[str(ctx.author.id)]["cryptos"][crypto] += 1 * amout
            data[str(ctx.author.id)]["cash"] -= items[crypto] * amout
        else:
            await response(ctx, f"You don't have enough money.")
    elif action == "sell":
        if data[str(ctx.author.id)]["cryptos"][crypto] >= amout:
            await response(ctx, f"You sold `{amout}x {crypto}` for `{items[crypto] * amout}{cashSymbol}`.")
            data[str(ctx.author.id)]["cryptos"][crypto] -= amout
            data[str(ctx.author.id)]["cash"] += items[crypto] * amout
        else:
            await response(ctx, f"You don't have enough `{crypto}s`.")
    
    writeData("Users", data)

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def leave(ctx: commands.Context):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await response(ctx, f"Left channel `{voice.channel}`")
        await voice.disconnect()
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def pause(ctx: commands.Context):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await response(ctx, f"Pausing playback in `{voice.channel}`")
        await voice.pause()
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def resume(ctx: commands.Context):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await response(ctx, f"Resuming playback in `{voice.channel}`")
        await voice.resume()
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def play(ctx: commands.Context, url: str):
    if url.find("music.youtube.com") != -1:
        filename = f"Sounds/{genHash(url)}.mp3"

        await response(ctx, f"Playing `{url}`")
        if not exists(filename):
            system(f"yt-dlp -x --audio-format mp3 -o {filename} \"{url}\"")
        await playSound(ctx.author, filename)
    else:
        await response(ctx, f"Invalid URL")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def tts(ctx: commands.Context, what: str, lang: str = "de"):
    filename = f"Sounds/{genHash(what+lang)}.mp3"

    await response(ctx, f"TTS message requested: `{lang[:2]}`\n```{what}```")
    if not exists(filename):
        gTTS(what, lang=lang[:2]).save(filename)
    await playSound(ctx.author, filename)

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def clear(ctx: commands.Context):
    if ctx.guild.get_role(1171129528849006719) in ctx.author.roles:
        await response(ctx, f"Clearing...")
        await ctx.channel.purge(limit=0xFFFF)
    else:
        await response(ctx, "You are not allow to do that!")

with open("token", "r") as tokenFile:
    bot.run(tokenFile.read())
