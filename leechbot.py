# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
from datetime import datetime
import asyncio, json, os
from methods import *

with open('token.json','r') as file:
    token = json.load(file)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


# bot initial. read existed party/log info
# partylog.json - all party members join/leave logs + buyer numbers after that + server time (utc) timestamp. and this can be used to generate currentparty.json, so this is the core file
partylog={}
if os.path.exists('partylog.json'):
    with open('partylog.json','r') as file:
        partylog = json.load(file)

party = get_currentparty(partylog)


log_lock = asyncio.Lock()
log = open
@bot.command()
async def join(ctx, ign):
    if str(ctx.author) == 't2julius':
        async with log_lock:
            result = join_party(partylog, party, ign)
            if result:
                await ctx.send(f'{ign} join party successful')
            else:
                await ctx.send(f'{ign} join party failed, he/she\'s already in party')

@bot.command()
async def leave(ctx, ign):
    if str(ctx.author) == 't2julius':
        async with log_lock:
            result = leave_party(partylog, party, ign)
            if result:
                await ctx.send(result)
            else:
                await ctx.send(f'{ign} leave party failed, he/she\'s not in party')

@bot.command()
async def undo(ctx):
    if str(ctx.author) == 't2julius':
        if undo_operation(partylog, party):
            await ctx.send('undo successful, last operation has been withdrawn')
        else:
            await ctx.send('undo failed, no last operation')

@bot.command()
async def ls(ctx):
    if str(ctx.author) == 't2julius':
        await ctx.send(f'party members: {party}')




bot.run(token['token'])