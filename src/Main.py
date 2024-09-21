from discord.ext import commands
from requests import post
from json import loads
import discord as dc

from SUtils import *

with open("Config.json", "r") as cfgFile:
  cfg = loads(cfgFile.read())

bot = commands.Bot(intents=dc.Intents.all())
soundQueue = []

async def response(ctx: commands.Context, msg: str, title: str = None, img: str = None):
  await ctx.respond(embed=dc.Embed(title=title, description=msg, thumbnail=img))

@bot.event
async def on_ready():
  await bot.change_presence(activity=dc.Activity(type=dc.ActivityType(cfg["Activity.Type"]), name=cfg["Activity.Name"]))
  sPrint("Main", f"Logged in as {bot.user} on {len(bot.guilds)} guild(s)!")

  sPrint("Cmd", "Syncronizing...")
  await bot.sync_commands(guild_ids=[guild.id for guild in bot.guilds])
  for cmd in bot.application_commands:
    sPrint("Cmd", f"Syncronized '{cmd.name}'")
  sPrint("Cmd", "Done.")

@bot.event
async def on_application_command(ctx: dc.ApplicationContext):
  sPrint("User", f"'{ctx.author.name}' used '{ctx.command.name}'")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def ping(ctx: dc.ApplicationContext):
  await response(ctx, f"Pong: {int(bot.latency * 1000)}ms")

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def clear(ctx: dc.ApplicationContext):
  if ctx.guild.get_role(1171129528849006719) in ctx.author.roles:
    await ctx.defer()
    await ctx.channel.purge(limit=0xFFFF)
    await response(ctx, "Cleared")
  else:
    await response(ctx, cfg["Error.NoPerm"])

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def ai(ctx: dc.ApplicationContext, prompt: str):
  content = ""
  json = {
    "model": "llama3.1",
    "prompt": prompt
  }

  if cfg["AI.System"] != "":
    json["system"] = cfg["AI.System"]

  await ctx.defer()
  with post(f"http://{cfg['AI.Host']}/api/generate", json=json) as request:
    await response(ctx, ".")
    for line in request.iter_lines():
      content += loads(line)["response"]
      await ctx.edit(embed=dc.Embed(description=content))

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def play(ctx: dc.ApplicationContext, url: str):
  await ctx.defer()

  soundQueue.append(fetchYtData(url))
  await response(ctx, "added to the queue", soundQueue[-1]["title"], soundQueue[-1]["thumbnail"])

  if ctx.guild.voice_client == None:
    await ctx.author.voice.channel.connect()
  else:
    return

  voice: dc.VoiceClient = ctx.guild.voice_client
  if voice == None:
    return

  while len(soundQueue) > 0:
    if voice.is_connected():
      await voice.play(dc.FFmpegOpusAudio(soundQueue[0]["url"]), wait_finish=True)
    
    soundQueue.pop(0)

  if voice.is_connected():
    await voice.disconnect()

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def stop(ctx: dc.ApplicationContext):
  voice: dc.VoiceClient = ctx.guild.voice_client
  if voice != None:
    await response(ctx, f"Left channel `{voice.channel}`")
    await voice.disconnect()
  else:
    await response(ctx, cfg["Error.Voice"])

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def pause(ctx: dc.ApplicationContext):
  voice: dc.VoiceClient = ctx.guild.voice_client
  if voice != None:
    await response(ctx, "paused", soundQueue[0]['title'], soundQueue[0]['thumbnail'])
    voice.pause()
  else:
    await response(ctx, cfg["Error.Voice"])

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def resume(ctx: dc.ApplicationContext):
  voice: dc.VoiceClient = ctx.guild.voice_client
  if voice != None:
    await response(ctx, "resumed", soundQueue[0]['title'], soundQueue[0]['thumbnail'])
    voice.resume()
  else:
    await response(ctx, cfg["Error.Voice"])

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def skip(ctx: dc.ApplicationContext):
  voice: dc.VoiceClient = ctx.guild.voice_client
  if voice != None:
    await response(ctx, "skiped", soundQueue[0]['title'], soundQueue[0]['thumbnail'])
    voice.stop()
  else:
    await response(ctx, cfg["Error.Voice"])

@bot.slash_command(guild_ids=[guild.id for guild in bot.guilds])
async def queue(ctx: dc.ApplicationContext):
  if len(soundQueue) > 0:
    await response(ctx, f"Queue:\n`{'\n'.join(song['title'] for song in soundQueue)}`")
  else:
    await response(ctx, cfg["Error.Queue"])

with open("token", "r") as tokenFile:
  bot.run(tokenFile.read())
