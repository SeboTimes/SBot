from discord.ext import commands, tasks
from os.path import exists
from os import system
from gtts import gTTS
import discord as dc

from Scripts.SFunctions import *
from Scripts.SData import *

bot = commands.Bot(intents=dc.Intents.all())

@tasks.loop(minutes=5)
async def priceUpdater():
    updatePrices()
    print("Prices", "Updated.")

@bot.event
async def on_ready():
    await bot.change_presence(activity=dc.Activity(type=dc.ActivityType.playing, name="with joe mama"))
    print("Main", f"Logged in as {bot.user} on {len(bot.guilds)} guild(s)!")

    print("Database", "Syncing users...")
    for guild in bot.guilds:
        async for member in guild.fetch_members():
            doMemberData(member)
    print("Database", "Done.")

    print("App", "Syncing commands...")
    await bot.sync_commands(guild_ids=[guild.id for guild in bot.guilds])
    for cmd in bot.application_commands:
        print("App", f"Synced '{cmd.name}'")
    print("App", "Done.")

    await priceUpdater.start()

@bot.event
async def on_member_join(member: dc.Member):
    doMemberData(member)

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def ping(ctx: commands.Context):
    await response(ctx, f"Pong: {int(bot.latency * 1000)}ms")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def wallet(ctx: commands.Context):
    data = readData("Users")
    await response(ctx, f"In your wallet are `{data[ctx.author.name]['cash']}{cashSymbol}`.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def inventory(ctx: commands.Context):
    data = readData("Users")
    outputs = {}
    for inventory in ["items", "cryptos"]:
        itemText = ""
        for item in data[ctx.author.name][inventory]:
            if data[ctx.author.name][inventory][item] > 0:
                itemText += f"\n`{data[ctx.author.name][inventory][item]}x {item}`"
        if len(itemText) > 0: outputs[inventory] = itemText
    
    msg = ""
    for output in outputs:
        msg += f"{output[0].upper()+output[1:]}: {outputs[output]}\n\n"

    if len(msg) > 0:
        await response(ctx, msg)
    else:
        await response(ctx, "Your inventory is empty.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def prices(ctx: commands.Context):
    output = {}
    for inventory in ["Items", "Cryptos"]:
        items = readData(inventory)
        itemText = ""
        for item in items:
            itemText += f"\n`{item}: {items[item]}{cashSymbol}`"
        output[inventory] = itemText

    await response(ctx, f"Item prices:{output['Items']}\n\nCrypto prices:{output['Cryptos']}")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
@dc.option("action", autocomplete=lambda: ["buy", "sell"])
@dc.option("item", autocomplete=lambda: [item for item in readData("Items")])
async def item(ctx: commands.Context, action: str, item: str, amout: int = 1):
    data = readData("Users")
    items = readData("Items")

    if action == "buy":
        if data[ctx.author.name]["cash"] >= items[item] * amout:
            await response(ctx, f"You bought `{amout}x {item}` for `{items[item] * amout}{cashSymbol}`.")
            data[ctx.author.name]["items"][item] += 1 * amout
            data[ctx.author.name]["cash"] -= items[item] * amout
        else:
            await response(ctx, f"You don't have enough money.")
    elif action == "sell":
        if data[ctx.author.name]["items"][item] >= amout:
            await response(ctx, f"You sold `{amout}x {item}` for `{items[item] * amout}{cashSymbol}`.")
            data[ctx.author.name]["items"][item] -= amout
            data[ctx.author.name]["cash"] += items[item] * amout
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
        if data[ctx.author.name]["cash"] >= items[crypto] * amout:
            await response(ctx, f"You bought `{amout}x {crypto}` for `{items[crypto] * amout}{cashSymbol}`.")
            data[ctx.author.name]["cryptos"][crypto] += 1 * amout
            data[ctx.author.name]["cash"] -= items[crypto] * amout
        else:
            await response(ctx, f"You don't have enough money.")
    elif action == "sell":
        if data[ctx.author.name]["cryptos"][crypto] >= amout:
            await response(ctx, f"You sold `{amout}x {crypto}` for `{items[crypto] * amout}{cashSymbol}`.")
            data[ctx.author.name]["cryptos"][crypto] -= amout
            data[ctx.author.name]["cash"] += items[crypto] * amout
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
