from rich import print as _print
from discord.ext import commands
from datetime import datetime
from mutagen.mp3 import MP3
from hashlib import sha256
from asyncio import sleep
import discord as dc

def print(owner: str, msg: str):
    _print(f"[bright_black]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bright_black] [blue bold]{owner}[/blue bold] {msg}")

def genHash(msg: str) -> str:
    return sha256(msg.encode()).hexdigest()

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
