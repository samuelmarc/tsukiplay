import os

from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()


class _Config:
    API_ID = int(os.getenv('API_ID'))  # https://my.telegram.org/
    API_HASH = os.getenv('API_HASH')  # https://my.telegram.org/
    BOT_TOKEN = os.getenv('BOT_TOKEN')  # https://t.me/BotFather
    WEB_APP = os.getenv('WEB_APP')  # Example: https://web-app.com
    SUDO_USERS = []  # users who can use admin commands (ex, notify)
    INLINE_CACHE = 5


config = _Config()
