import asyncio

import discord
import discord.utils
from discord.ext import commands

from .model import RankedVote


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='-', intents=intents)

open_votes = {}


class Emoji:

    CONFIRM = '✅'
    CANCEL = '❎'
    ONE = '1️⃣'
    TWO = '2️⃣'
    THREE = '3️⃣'
    FOUR = '4️⃣'
    FIVE = '5️⃣'
    SIX = '6️⃣'
    SEVEN = '7️⃣'
    EIGHT = '8️⃣'
    NINE = '9️⃣'
    TEN = '🔟'

    @staticmethod
    def statuses():
        return [Emoji.CONFIRM, Emoji.CANCEL]

    @staticmethod
    def numbers():
        return [Emoji.ONE, Emoji.TWO, Emoji.THREE, Emoji.FOUR, Emoji.FIVE,
                Emoji.SIX, Emoji.SEVEN, Emoji.EIGHT, Emoji.NINE, Emoji.TEN]


async def get_create_vote_response(ctx, name):
    message = await ctx.send(f'Tell me about the next choice for {name}, or react to this message to finish.')
    await message.add_reaction(Emoji.CONFIRM)
    await message.add_reaction(Emoji.CANCEL)

    while True:
        done, pending = await asyncio.wait([
            bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author),
            bot.wait_for('reaction_add', check=lambda reaction, user: user == ctx.author and reaction.message == message)
        ], return_when=asyncio.FIRST_COMPLETED)
        result = next(iter(done)).result()

        if isinstance(result, discord.Message) and result.author == ctx.author:
            return result
        elif result[1] == ctx.author and result[0].message == message and str(result[0].emoji) in Emoji.statuses():
            return result


@bot.command('create-vote')
async def create_vote(ctx, *args):
    if len(args) != 1:
        await ctx.send('Usage: -create-vote "{name}"')
        return

    name = args[0]

    if (ctx.guild, name) in open_votes:
        await ctx.send(f'There is already an open vote named {name}')
        return

    choices = []
    while True:
        response = await get_create_vote_response(ctx, name)
        if isinstance(response, discord.Message):
            choices.append(response.content)
        elif str(response[0].emoji) == Emoji.CONFIRM:
            await ctx.send('\n'.join([
                f'Vote created: {name}',
                *(f'{i+1}. {choice}' for i, choice in enumerate(choices))
            ]))
            open_votes[(ctx.guild, name)] = RankedVote(name, choices)

            return
        elif str(response[0].emoji) == Emoji.CANCEL:
            await ctx.send(f'Vote cancelled: {name}')
            return


def str_choice_index(i):
    if i % 10 == 1:
        return f'{i}st'
    elif i % 10 == 2:
        return f'{i}nd'
    elif i % 10 == 3:
        return f'{i}rd'
    else:
        return f'{i}th'


async def get_vote_response(member, vote, choice_index):
    dm = await member.send(f'What is your **{str_choice_index(choice_index)}** choice? Enter an index or react {Emoji.CONFIRM} to this message to submit your vote.')
    await dm.add_reaction(Emoji.CONFIRM)

    while True:
        done, pending = await asyncio.wait([
            bot.wait_for('message', check=lambda message: message.channel == dm.channel),
            bot.wait_for('reaction_add', check=lambda reaction, user: user == member and reaction.message == dm and str(reaction.emoji) == Emoji.CONFIRM)
        ], return_when=asyncio.FIRST_COMPLETED)

        result = next(iter(done)).result()
        return result


async def get_choices(vote, member):
    await member.send(f'{vote.name} is now open for voting! Your choices are:')
    messages = []
    for i, choice in enumerate(vote.choices):
        message = await member.send(f'{i + 1}. {choice}')
        messages.append(message)
    confirm_msg = await member.send('React to each message with your rank for that choice. You don\'t have to rank every choice.\nReact ✅ to this message to submit your vote.')
    await confirm_msg.add_reaction(Emoji.CONFIRM)

    await asyncio.gather(*(
        message.add_reaction(Emoji.ONE)
        for message in messages
    ))

    last_rank = 0
    while True:
        reaction, user = await bot.wait_for('reaction_add', check=lambda reaction, user: user == member and reaction.message in [*messages, confirm_msg])
        emoji = str(reaction.emoji)
        if reaction.message == confirm_msg and emoji == Emoji.CONFIRM:
            break
        if emoji not in Emoji.numbers():
            continue

        rank = Emoji.numbers().index(emoji)
        if rank == last_rank and rank < len(vote.choices) - 1:
            last_rank += 1
            await asyncio.gather(*(
                message.add_reaction(Emoji.numbers()[last_rank])
                for message in messages
            ))

    await member.send(f'Your vote has been recorded. Thank you for voting!')


@bot.command('open-vote')
async def start_vote(ctx, *args):
    if len(args) != 2:
        await ctx.send('Usage: -open-vote "{name}" "{role}"')
        return

    # Validate vote
    try:
        vote = open_votes[(ctx.guild, args[0])]
    except KeyError:
        await ctx.send(f'{args[0]} is not an open vote.')
        return

    if vote.has_started:
        await ctx.send(f'{args[0]} is already open for voting.')

    # Validate role
    role = discord.utils.get(ctx.guild.roles, name=args[1])
    if not role:
        await ctx.send(f'{args[1]} is not a role.')
        return

    # Slide into members' DM's ;)
    await ctx.send(f'{vote.name} has opened for voting! Users which are eligible to vote will be messaged. Use -close-vote "{{name}}" to close the vote and view the results.')

    vote.has_started = True

    members = [member for member in ctx.guild.members if role in member.roles]
    await asyncio.gather(*(get_choices(vote, member) for member in members))
