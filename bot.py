import asyncio
from os import listdir
from os.path import isfile, join

import discord
import motor.motor_asyncio
from discord.ext import commands

import utils.globals as GG
from utils import logger

MDB = motor.motor_asyncio.AsyncIOMotorClient(GG.MONGODB)['']

log = logger.logger

SHARD_COUNT = 1
TESTING = True
defaultPrefix = GG.PREFIX if not TESTING else '*'


def get_prefix(b, message):
    if not message.guild:
        return commands.when_mentioned_or(defaultPrefix)(b, message)
    gp = b.prefixes.get(str(message.guild.id), defaultPrefix)
    return commands.when_mentioned_or(gp)(b, message)


class Crawler(commands.AutoShardedBot):
    def __init__(self, prefix, help_command=None, description=None, **options):
        super(Crawler, self).__init__(prefix, help_command, description, **options)
        self.owner = None
        self.testing = TESTING
        self.state = "init"
        if self.testing:
            self.token = GG.TESTTOKEN
        else:
            self.token = GG.TOKEN
        self.prefixes = dict()
        self.mdb = MDB
        self.version = 0

    async def get_server_prefix(self, msg):
        return (await get_prefix(self, msg))[-1]

    async def launch_shards(self):
        if self.shard_count is None:
            recommended_shards, _ = await self.http.get_bot_gateway()
            if recommended_shards >= 96 and not recommended_shards % 16:
                # half, round up to nearest 16
                self.shard_count = recommended_shards // 2 + (16 - (recommended_shards // 2) % 16)
            else:
                self.shard_count = recommended_shards // 2
        log.info(f"Launching {self.shard_count} shards!")
        await super(Crawler, self).launch_shards()


bot = Crawler(prefix=get_prefix, case_insensitive=True, status=discord.Status.idle,
              description="A bot.", shard_count=SHARD_COUNT, testing=TESTING,
              activity=discord.Game(f"!help | Initializing..."))


@bot.event
async def on_ready():
    bot.version = await GG.get_statistic(bot.mdb, "version")
    await bot.change_presence(activity=discord.Game(f"with {len(bot.guilds)} servers | !help | v{bot.version}"),
                              afk=True)
    print(f"Logged in as {bot.user.name} ({bot.user.id})")


@bot.event
async def on_connect():
    bot.owner = await bot.fetch_user(GG.OWNER)
    print(f"OWNER: {bot.owner.name}")


@bot.event
async def on_resumed():
    log.info('resumed.')


def loadCogs():
    i = 0
    log.info("Loading Cogs...")
    for extension in [f.replace('.py', '') for f in listdir(GG.COGS) if isfile(join(GG.COGS, f))]:
        try:
            bot.load_extension(GG.COGS + "." + extension)
        except Exception as e:
            log.error(f'Failed to load extension {extension}')
            i += 1
    log.info("-------------------")
    log.info("Loading Event Cogs...")
    for extension in [f.replace('.py', '') for f in listdir(GG.COGSEVENTS) if isfile(join(GG.COGSEVENTS, f))]:
        try:
            bot.load_extension(GG.COGSEVENTS + "." + extension)
        except Exception as e:
            log.error(f'Failed to load extension {extension}')
            i += 1
    log.info("-------------------")
    if i == 0:
        log.info("Finished Loading All Cogs...")
    else:
        log.info(f"Finished Loading Cogs with {i} errors...")

if __name__ == "__main__":
    bot.state = "run"
    loadCogs()
    bot.run(bot.token)
