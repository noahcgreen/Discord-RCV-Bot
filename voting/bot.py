import asyncio
import hashlib

import discord
import discord.utils
from discord.ext import commands

from .model import RankedVote


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='-', intents=intents)

active_conversations = {}


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if (message.channel, message.author) in active_conversations:
        conversation = active_conversations[(message.channel, message.author)]
        try:
            await conversation.asend(message)
        except StopAsyncIteration:
            del active_conversations[(message.channel, message.author)]

        return

    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    try:
        conversation = active_conversations[(reaction.message.channel, user)]
    except KeyError:
        return


async def create_vote_conversation(ctx, name):
    while True:
        await ctx.send(f'Tell me about the next choice for {name}, or react to this message to finish.')
        message = yield
        if message == 'confirm':
            await ctx.send('Ok, your vote is set up!')
            break
        elif message == 'cancel':
            await ctx.send('Your vote has been cancelled.')
            break
        else:
            await ctx.send("Ok, I've added this choice to the vote.")


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
    choices = []
    while True:
        response = await get_create_vote_response(ctx, name)
        if isinstance(response, discord.Message):
            choices.append(response.content)
        elif str(response[0].emoji) == '✅':
            await ctx.send('\n'.join([
                f'Vote confirmed: {name}',
                'Your options are:',
                *(f'{i+1}. {choice}' for i, choice in enumerate(choices))
            ]))
            vote = RankedVote(name, choices)
            return
        elif str(response[0].emoji) == '❎':
            await ctx.send(f'Vote cancelled: {name}')
            return
