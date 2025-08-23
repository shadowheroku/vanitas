from platform import python_version
from threading import RLock
from time import gmtime, strftime
from time import time as t

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram.types import BotCommand

from Powers import (
    API_HASH, API_ID, BOT_TOKEN, LOG_DATETIME, LOGGER,
    NO_LOAD, UPTIME, WORKERS, load_cmds, scheduler
)
from Powers.database import MongoDB
from Powers.plugins import all_plugins
from Powers.plugins.scheduled_jobs import *
from Powers.supports import *
from Powers.vars import Config

INITIAL_LOCK = RLock()


class Gojo(Client):
    """Starts the Pyrogram Client on the Bot Token when we do 'python3 -m Powers'"""

    def __init__(self):
        super().__init__(
            "Gojo_Satoru",
            bot_token=BOT_TOKEN,
            plugins=dict(root="Powers.plugins", exclude=NO_LOAD),
            api_id=API_ID,
            api_hash=API_HASH,
            workers=WORKERS,
        )

    async def start(self):
        """Start the bot."""
        await super().start()

        await self.set_bot_commands(
            [
                BotCommand("start", "To check whether the bot is alive"),
                BotCommand("help", "To get help menu"),
                BotCommand("donate", "To buy me a coffee"),
                BotCommand("bug", "To report bugs"),
            ]
        )

        meh = await self.get_me()
        LOGGER.info("Starting bot...")
        Config.BOT_ID = meh.id
        Config.BOT_NAME = meh.first_name
        Config.BOT_USERNAME = meh.username

        LOGGER.info(
            f"Pyrogram v{__version__} (Layer - {layer}) started on {meh.username}",
        )
        LOGGER.info(f"Python Version: {python_version()}\n")

        # Load plugins and support users
        cmd_list = await load_cmds(await all_plugins())
        await load_support_users()
        await cache_support()
        LOGGER.info(f"Dev Users: {SUPPORT_USERS['Dev']}")
        LOGGER.info(f"Sudo Users: {SUPPORT_USERS['Sudo']}")
        LOGGER.info(f"Whitelist users: {SUPPORT_USERS['White']}")
        LOGGER.info(f"Plugins Loaded: {cmd_list}")

        # Schedule birthday jobs if enabled
        if BDB_URI:
            scheduler.add_job(send_wishish, "cron", [self], hour=0, minute=0, second=0)
            scheduler.start()

        LOGGER.info("Bot Started Successfully!\n")

    async def stop(self):
        """Stop the bot and cleanup."""
        runtime = strftime("%Hh %Mm %Ss", gmtime(t() - UPTIME))
        LOGGER.info("Stopping bot...")

        scheduler.remove_all_jobs()
        await super().stop()
        MongoDB.close()

        LOGGER.info(
            f"""Bot Stopped.
            Runtime: {runtime}
            Logs saved at {LOG_DATETIME}
        """,
        )
