import discord, json
from discord.ext import commands
from command_handler import BotCommandHandler
from data_manager import LogEntry, DataManager

with open('token.json', 'r') as file:
    token = json.load(file)

ADMIN_USERS = ['t2julius']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)
data_manager = DataManager()
command_handler = BotCommandHandler(data_manager)

@bot.command()
async def join(ctx, ign):
    await command_handler.join(ctx, ign)

@bot.command()
async def leave(ctx, ign):
    await command_handler.leave(ctx, ign)

@bot.command()
async def pause(ctx):
    await command_handler.pause(ctx)

@bot.command()
async def resume(ctx):
    await command_handler.resume(ctx)

@bot.command()
async def undo(ctx):
    await command_handler.undo(ctx)


@bot.command()
async def party(ctx):
    await command_handler.party(ctx)

bot.run(token['token'])
