import asyncio
import hashlib

import discord
import discord.utils
from discord.ext import commands

from .model import RankedVote


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='-', intents=intents)

open_votes = {}


async def get_create_vote_response(ctx, name):
    message = await ctx.send(f'Tell me about the next choice for {name}, or react to this message to finish.')
    await message.add_reaction('✅')
    await message.add_reaction('❎')

    while True:
        done, pending = await asyncio.wait([
            bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author),
            bot.wait_for('reaction_add', check=lambda r, user: user == ctx.author)
        ], return_when=asyncio.FIRST_COMPLETED)
        result = next(iter(done)).result()

        if isinstance(result, discord.Message) and result.author == ctx.author:
            return result
        elif result[1] == ctx.author and result[0].message == message and str(result[0].emoji) in ['✅', '❎']:
            return result


@bot.command('create-vote')
async def create_vote(ctx, *args):
    if len(args) < 1:
        await ctx.send('You most provide a name!\nE.g. -create-vote {name}')
        return

    name = ' '.join(args)

    if (ctx.guild, name) in open_votes:
        await ctx.send(f'There is already an open vote named {name}')
        return

    choices = []
    while True:
        response = await get_create_vote_response(ctx, name)
        if isinstance(response, discord.Message):
            choices.append(response.content)
            await response.add_reaction('👍')
        elif str(response[0].emoji) == '✅':
            await ctx.send('\n'.join([
                f'Vote created: {name}',
                *(f'{i+1}. {choice}' for i, choice in enumerate(choices))
            ]))
            open_votes[(ctx.guild, name)] = RankedVote(name, choices)
            return
        elif str(response[0].emoji) == '❎':
            await ctx.send(f'Vote cancelled: {name}')
            return
