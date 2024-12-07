import aiosqlite

STRUCTURE = '''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER NOT NULL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS animes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT NOT NULL UNIQUE
);
'''


class _Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        conn = await aiosqlite.connect('database.db')
        conn.row_factory = aiosqlite.Row
        await conn.execute('VACUUM')
        await conn.execute('PRAGMA journal_mode=WAL')
        await conn.executescript(STRUCTURE)
        await conn.commit()
        self.conn = conn

    async def close(self):
        if self.conn:
            await self.conn.close()


database = _Database()
