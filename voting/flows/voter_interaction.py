import asyncio
import collections
import math

import pyrankvote

from voting.util import Emoji


async def get_ranks(user, messages):
    ranks = []
    for i, message in enumerate(messages):
        ranks.append([])
        for reaction in message.reactions:
            if str(reaction.emoji) in Emoji.numbers() and user in await reaction.users().flatten():
                rank = Emoji.numbers().index(str(reaction.emoji)) + 1
                if 0 < rank <= len(messages):
                    ranks[i].append(rank)
    return ranks


def validate(ranks, vote):
    errors = []
    # Only one rank per choice
    for i, rank_list in enumerate(ranks):
        if len(rank_list) > 1:
            errors.append(f'Choice {i+1} has multiple ranks assigned.')
    actual_ranks = [rank_list[0] for rank_list in ranks if rank_list]

    counter = collections.Counter(actual_ranks)
    # Can't skip ranks
    for i in range(max(actual_ranks)):
        if counter[i+1] == 0:
            errors.append(f'Rank {i+1} has been skipped.')
            break
    # Can't assign same rank to two choices
    for i in range(len(ranks)):
        if counter[i+1] > 1:
            errors.append(f'Rank {i+1} has been assigned more than once.')

    choices = [None] * max(actual_ranks)
    for i, rank in enumerate(ranks):
        if rank:
            choices[rank[0] - 1] = vote.choices[i]
    ballot = pyrankvote.Ballot(ranked_candidates=choices)
    return ballot, errors


async def get_choices(ctx, vote, member):
    await member.send(f'{vote.name} is now open for voting! Your choices are:')
    messages = []
    for i, choice in enumerate(vote.choices):
        message = await member.send(f'{i + 1}. {choice.name}')
        messages.append(message)
    confirm_msg = await member.send(f'React to each message with your rank for that choice. You don\'t have to rank every choice.\nReact {Emoji.CONFIRM} to this message to submit your vote.')
    await confirm_msg.add_reaction(Emoji.CONFIRM)

    await asyncio.gather(*(
        message.add_reaction(Emoji.ONE)
        for message in messages
    ))

    last_rank = 0
    while True:
        def check(reaction, user):
            return user == member and reaction.message in [*messages, confirm_msg]

        reaction, user = await ctx.bot.wait_for('reaction_add', check=check)
        emoji = str(reaction.emoji)
        if reaction.message == confirm_msg and emoji == Emoji.CONFIRM:
            messages = await asyncio.gather(*(
                member.dm_channel.fetch_message(message.id)
                for message in messages
            ))
            ballot, errors = validate(await get_ranks(member, messages), vote)
            if errors:
                confirm_msg = await member.send('\n'.join(['Please fix the following errors:', *errors]))
            else:
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

    if vote.has_ended:
        await member.send('This vote has already ended.')
        return

    vote.ballots.append(ballot)
    await member.send(f'Your vote has been recorded. Thank you for voting!')
