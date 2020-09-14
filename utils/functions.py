import logging
import random
import re

import discord

log = logging.getLogger(__name__)


class SearchException(Exception):
    pass


async def splitDiscordEmbedField(embed, input, embed_field_name):
    texts = []
    while len(input) > 1024:
        next_text = input[:1024]
        last_space = next_text.rfind(" ")
        input = "…" + input[last_space + 1:]
        next_text = next_text[:last_space] + "…"
        texts.append(next_text)
    texts.append(input)
    embed.add_field(name=embed_field_name, value=texts[0], inline=False)
    for piece in texts[1:]:
        embed.add_field(name="** **", value=piece, inline=False)


async def safeEmbed(embed_queue, title, desc, color):
    if len(desc) < 1024:
        embed_queue[-1].add_field(name=title, value=desc, inline=False)
    elif len(desc) < 4096:
        embed = discord.Embed(colour=color, title=title)
        await splitDiscordEmbedField(embed, desc, title)
        embed_queue.append(embed)
    else:
        embed_queue.append(discord.Embed(colour=color, title=title))
        trait_all = [desc[i:i + 4080] for i in range(0, len(desc), 4080)]
        embed_queue[-1].description = trait_all[0]
        for t in trait_all[1:]:
            embed = discord.Embed(colour=color)
            await splitDiscordEmbedField(embed, t, "** **")
            embed_queue.append(embed)


def gen_error_message():
    subject = random.choice(['A kobold', 'The green dragon', 'The Frost Mage', 'DiscordCrawler', 'The wizard',
                             'An iron golem', 'Your mom', 'This bot', 'You', 'Me', 'The president',
                             'The Queen', 'Xanathar', 'Volo', 'This world'])
    verb = random.choice(['must be', 'should be', 'has been', 'will be', 'is being', 'was being'])
    thing_to_do = random.choice(['stopped', 'killed', 'talked to', 'found', 'destroyed', 'fought'])
    return f"{subject} {verb} {thing_to_do}"


def a_or_an(string, upper=False):
    if string.startswith('^') or string.endswith('^'):
        return string.strip('^')
    if re.match('[AEIOUaeiou].*', string):
        return 'an {0}'.format(string) if not upper else f'An {string}'
    return 'a {0}'.format(string) if not upper else f'A {string}'


def camel_to_title(string):
    return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', string).title()
