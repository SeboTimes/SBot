from discord.ext import commands
from os.path import exists
from os import system
import discord as dc

from Scripts import Startup
from Scripts.SFunctions import *
from Scripts.SData import *

bot = commands.Bot(intents=dc.Intents.all())

_queue = []

@bot.event
async def on_ready():
    await bot.change_presence(activity=dc.Activity(type=dc.ActivityType.playing, name="with your life"))
    sPrint("Main", f"Logged in as {bot.user} on {len(bot.guilds)} guild(s)!")

    sPrint("Database", "Syncing users...")
    for guild in bot.guilds:
        async for member in guild.fetch_members():
            doMemberData(member)
    sPrint("Database", "Done.")

    sPrint("App", "Syncing commands...")
    await bot.sync_commands(guild_ids=[guild.id for guild in bot.guilds])
    for cmd in bot.application_commands:
        sPrint("App", f"Synced '{cmd.name}'")
    sPrint("App", "Done.")

@bot.event
async def on_member_join(member: dc.Member):
    doMemberData(member)

@bot.event
async def on_application_command(ctx: dc.ApplicationContext):
    sPrint("User", f"'{ctx.author.name}' used '{ctx.command.name}'")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def ping(ctx: dc.ApplicationContext):
    await response(ctx, f"Pong: {int(bot.latency * 1000)}ms")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def wallet(ctx: dc.ApplicationContext):
    data = readData("Users")
    await response(ctx, f"In your wallet are `{data[ctx.author.name]['cash']}€`.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def stop(ctx: dc.ApplicationContext):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await ctx.defer()
        await voice.disconnect()
        await response(ctx, f"Left channel `{voice.channel}`")
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def pause(ctx: dc.ApplicationContext):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await ctx.defer()
        voice.pause()
        await response(ctx, f"Paused `{fetchYtData(_queue[0])}` in `{voice.channel}`")
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def resume(ctx: dc.ApplicationContext):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await ctx.defer()
        voice.resume()
        await response(ctx, f"Resumed `{fetchYtData(_queue[0])}` in `{voice.channel}`")
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def skip(ctx: dc.ApplicationContext):
    voice: dc.VoiceClient = ctx.guild.voice_client
    if voice != None:
        await ctx.defer()
        voice.stop()
        await response(ctx, f"Skiped `{fetchYtData(_queue[0])}` in `{voice.channel}`")
    else:
        await response(ctx, f"Bot is currently not in a voice channel")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def play(ctx: dc.ApplicationContext, url: str):
    if url.find("music.youtube.com") != -1:
        url = url.split("&")[0]
    else:
        url = url.split("?")[0]

    _queue.append(url)

    await ctx.defer()
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
                system(f"yt-dlp -x --audio-format mp3 -o \"{filename}\" \"{_queue[0]}\"")
            await voice.play(dc.FFmpegPCMAudio(filename), wait_finish=True)
        
        _queue.pop(0)

    if voice.is_connected():
        await voice.disconnect()

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def queue(ctx: dc.ApplicationContext):
    if len(_queue) > 0:
        await ctx.defer()
        await response(ctx, f"Queue:\n`{"\n".join(fetchYtData(song) for song in _queue)}`")
    else:
        await response(ctx, "Queue is empty.")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def clear(ctx: dc.ApplicationContext):
    if ctx.guild.get_role(1171129528849006719) in ctx.author.roles:
        await ctx.defer()
        await ctx.channel.purge(limit=0xFFFF)
        await response(ctx, f"Cleared")
    else:
        await response(ctx, "You are not allow to do that!")

with open("token", "r") as tokenFile:
    bot.run(tokenFile.read())
