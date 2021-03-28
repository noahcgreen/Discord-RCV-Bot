import asyncio

import discord
import pyrankvote

from voting import data
from voting.model import RankedVote
from voting.util import Emoji


async def get_create_vote_response(ctx, name):
    message = await ctx.send(f'Tell me about the next choice for {name}, or react to this message to finish.')
    await message.add_reaction(Emoji.CONFIRM)
    await message.add_reaction(Emoji.CANCEL)

    while True:
        done, pending = await asyncio.wait([
            ctx.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author),
            ctx.bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message == message)
        ], return_when=asyncio.FIRST_COMPLETED)
        result = next(iter(done)).result()

        if isinstance(result, discord.Message) and result.author == ctx.author:
            return result
        elif result[1] == ctx.author and result[0].message == message and str(result[0].emoji) in Emoji.statuses():
            return result


async def create_vote(ctx, *args):
    if len(args) != 1:
        await ctx.send('Usage: -create-vote "{name}"')
        return

    name = args[0]

    if (ctx.guild, name) in data.open_votes:
        await ctx.send(f'There is already an open vote named {name}')
        return

    choices = []
    while True:
        response = await get_create_vote_response(ctx, name)
        if isinstance(response, discord.Message):
            choices.append(pyrankvote.Candidate(response.content))
        elif str(response[0].emoji) == Emoji.CONFIRM:
            await ctx.send('\n'.join([
                f'Vote created: {name}',
                *(f'{i+1}. {choice.name}' for i, choice in enumerate(choices))
            ]))
            data.open_votes[(ctx.guild, name)] = RankedVote(name, choices)

            return
        elif str(response[0].emoji) == Emoji.CANCEL:
            await ctx.send(f'Vote cancelled: {name}')
            return
