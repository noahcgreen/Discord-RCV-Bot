import pyrankvote

from voting import data


async def close_vote(ctx, *args):
    if len(args) != 1:
        await ctx.send('Usage: -vote close {name}')
        return

    name = args[0]
    try:
        vote = data.open_votes[(ctx.guild, name)]
    except KeyError:
        await ctx.send(f'No vote named {name}')
        return

    if not vote.has_started:
        await ctx.send(f'{name} has not opened yet.')
        return

    if vote.has_ended:
        await ctx.send(f'{name} has already been closed.')
        return

    vote.has_ended = True
    del data.open_votes[(ctx.guild, name)]

    await ctx.send(f'Voting for {name} has been closed. Results will be posted when available.')

    result = pyrankvote.instant_runoff_voting(vote.choices, vote.ballots)
    await ctx.send(str(result))

