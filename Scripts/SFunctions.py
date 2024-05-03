from discord.ext import commands
from datetime import datetime
from hashlib import sha256
from asyncio import sleep
import discord as dc

_print = print

def print(owner: str, msg: str):
    _print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{owner}] {msg}")

def genHash(msg: str) -> str:
    return sha256(msg.encode()).hexdigest()

async def response(ctx: commands.Context, msg: str):
    await ctx.respond(embed=dc.Embed(description=msg))
