import discord
from discord.ext import commands


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

    await bot.process_commands(message)


async def create_vote_conversation(ctx, name):
    await ctx.send(f'Tell me about the next choice for {name}, or react to this message to finish.')
    message = yield
    await ctx.send('kk')
    await ctx.send(message.content)


@bot.command('create-vote')
async def create_vote(ctx, *args):
    if len(args) < 1:
        await ctx.send('You most provide a name!\nE.g. -create-vote {name}')
        return

    name = ' '.join(args)
    conversation = create_vote_conversation(ctx, name)
    active_conversations[(ctx.channel, ctx.author)] = conversation
    await conversation.asend(None)
