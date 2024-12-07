import os

from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()


class _Config:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEB_APP = os.getenv('WEB_APP')  # users who can use admin commands (e.g. notify)# Example: https://web-app.com
    SUDO_USERS = []  # users who can use admin commands (ex, notify)
    INLINE_CACHE = 5


config = _Config()
