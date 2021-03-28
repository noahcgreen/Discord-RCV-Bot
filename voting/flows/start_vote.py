import asyncio

import discord

from voting import data
from voting.flows.voter_interaction import get_choices


async def start_vote(ctx, *args):
    if len(args) != 2:
        await ctx.send('Usage: -open-vote "{name}" "{role}"')
        return

    # Validate vote
    try:
        vote = data.open_votes[(ctx.guild, args[0])]
    except KeyError:
        await ctx.send(f'{args[0]} is not an open vote.')
        return

    if vote.has_started:
        await ctx.send(f'{args[0]} is already open for voting.')
        return

    # Validate role
    role = discord.utils.get(ctx.guild.roles, name=args[1])
    if not role:
        await ctx.send(f'{args[1]} is not a role.')
        return

    # Slide into members' DM's ;)
    await ctx.send(f'{vote.name} has opened for voting! Users which are eligible to vote will be messaged. Use -close-vote "{{name}}" to close the vote and view the results.')

    vote.has_started = True

    members = [member for member in ctx.guild.members if role in member.roles]
    await asyncio.gather(*(get_choices(ctx, vote, member) for member in members))