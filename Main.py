from discord.ext import commands, tasks
from os.path import exists
from os import system
import discord as dc

from Scripts import Startup
from Scripts.SFunctions import *
from Scripts.SData import *

bot = commands.Bot(intents=dc.Intents.all())

_queue = []

@tasks.loop(minutes=5)
async def priceUpdater():
    updatePrices()
    print("Prices", "Updated.")

@bot.event
async def on_ready():
    await bot.change_presence(activity=dc.Activity(type=dc.ActivityType.playing, name="with your life"))
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

@bot.event
async def on_application_command(ctx: commands.Context):
    print("User", f"'{ctx.author.name}' used '{ctx.command.name}'")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def ping(ctx: commands.Context):
    await response(ctx, f"Pong: {int(bot.latency * 1000)}ms")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def wallet(ctx: commands.Context):
    data = readData("Users")
    await response(ctx, f"In your wallet are `{data[ctx.author.name]['cash']}€`.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def inventory(ctx: commands.Context):
    await response(ctx, f"Your Inventory:\n{"\n".join([f"`{key}: {value}`" for (key, value) in readData("Users")[ctx.author.name]["cryptos"].items()])}")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def prices(ctx: commands.Context):
    await response(ctx, f"Crypto prices:\n{"\n".join([f"`{key}: {value}€`" for (key, value) in readData("Cryptos").items()])}")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
@dc.option("action", autocomplete=lambda x: ["buy", "sell"])
@dc.option("crypto", autocomplete=lambda x: [crypto for crypto in readData("Cryptos")])
async def crypto(ctx: commands.Context, action: str, crypto: str, amout: int = 1):
    data = readData("Users")
    items = readData("Cryptos")

    if action == "buy":
        if data[ctx.author.name]["cash"] >= items[crypto] * amout:
            await response(ctx, f"You bought `{amout}x {crypto}` for `{items[crypto] * amout}€`.")
            data[ctx.author.name]["cryptos"][crypto] += 1 * amout
            data[ctx.author.name]["cash"] -= items[crypto] * amout
        else:
            await response(ctx, f"You don't have enough money.")
    elif action == "sell":
        if data[ctx.author.name]["cryptos"][crypto] >= amout:
            await response(ctx, f"You sold `{amout}x {crypto}` for `{items[crypto] * amout}€`.")
            data[ctx.author.name]["cryptos"][crypto] -= amout
            data[ctx.author.name]["cash"] += items[crypto] * amout
        else:
            await response(ctx, f"You don't have enough `{crypto}s`.")
    
    writeData("Users", data)

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def stop(ctx: commands.Context):
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
        await response(ctx, f"Pausing `{queue[0]}` in `{voice.channel}`")
        voice.pause()
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def resume(ctx: commands.Context):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await response(ctx, f"Resuming `{queue[0]}` in `{voice.channel}`")
        voice.resume()
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def skip(ctx: commands.Context):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await response(ctx, f"Skiped `{queue[0]}` in `{voice.channel}`")
        voice.stop()
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def play(ctx: commands.Context, url: str):
    if url.find("music.youtube.com") != -1:
        _queue.append(url)
        await response(ctx, f"Added `{fetchYtData(url)}` to the queue.")

        if ctx.guild.voice_client == None:
            await ctx.author.voice.channel.connect()
        else:
            return

        voice: dc.VoiceClient = ctx.guild.voice_client
        if voice == None:
            return

        while len(_queue) > 0:
            filename = f"Sounds/{genHash(fetchYtData(_queue[0]))}.mp3"

            if voice.is_connected():
                if not exists(filename):
                    system(f"yt-dlp -x --audio-format mp3 -o {filename} \"{_queue[0]}\"")
                await voice.play(dc.FFmpegPCMAudio(filename), wait_finish=True)
            
            _queue.pop(0)

        if voice.is_connected():
            await voice.disconnect()
    else:
        await response(ctx, f"Invalid URL")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def queue(ctx: commands.Context):
    if len(_queue) > 0:
        await response(ctx, f"Queue:\n`{"\n".join(fetchYtData(song) for song in _queue)}`")
    else:
        await response(ctx, "Queue is empty.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def clear(ctx: commands.Context):
    if ctx.guild.get_role(1171129528849006719) in ctx.author.roles:
        await response(ctx, f"Clearing...")
        await ctx.channel.purge(limit=0xFFFF)
    else:
        await response(ctx, "You are not allow to do that!")

with open("token", "r") as tokenFile:
    bot.run(tokenFile.read())
