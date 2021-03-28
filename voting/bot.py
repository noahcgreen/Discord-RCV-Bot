import discord.utils
from discord.ext import commands

from voting.flows.close_vote import close_vote
from voting.flows.create_vote import create_vote
from voting.flows.start_vote import start_vote


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='-', intents=intents)


@bot.group('vote')
async def vote(ctx):
    pass


vote.command('create')(create_vote)
vote.command('open')(start_vote)
vote.command('close')(close_vote)
