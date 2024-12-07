from pyromod import Client
from pyrogram import idle
from pyrogram.enums import ParseMode

from config import config
from database import database

app = Client(
    'tsukiplay',
    config.API_ID,
    config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins={'root': 'plugins'},
    parse_mode=ParseMode.MARKDOWN
)


async def main():
    await database.connect()
    await app.start()
    print('Bot started.')
    await idle()
    await app.stop()
    await database.close()
    print('Bot stopped.')

app.run(main())
