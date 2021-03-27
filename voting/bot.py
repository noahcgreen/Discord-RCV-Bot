import discord
from discord.ext import commands


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='-', intents=intents)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     print(message.content)
#
#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')
#         await message.author.send('Hi!')
#
#     await bot.process_commands(message)


@bot.command('create-vote')
async def create_vote(ctx, *args):
    if len(args) < 1:
        await ctx.send('You most provide a name!\nE.g. -create-vote {name}')
        return

    name = ' '.join(args)
    print(f'Creating vote named {name}')
