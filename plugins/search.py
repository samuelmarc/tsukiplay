from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
from pyromod import ikb

from animes import search_anime
from config import config
from database import database


@Client.on_inline_query(filters.regex('^.+$'))
async def inline(_, q: InlineQuery):
    query = q.query
    offset = int(q.offset or 0) + 24
    page = int(offset / 20)
    results = await search_anime(query, page)
    if results:
        conn = database.conn
        async with conn.cursor() as cur:
            for result in results['results']:
                path = result['path']
                await cur.execute('SELECT id FROM animes WHERE alias = ?', (path,))
                ch = await cur.fetchone()
                if ch:
                    del result['path']
                    result['id'] = ch['id']
                else:
                    await cur.execute('INSERT INTO animes (alias) VALUES (?)', (path,))
                    del result['path']
                    result['id'] = cur.lastrowid
                    await conn.commit()

        if page == results['max_pages']:
            offset = None
        else:
            offset = str(offset)

        results = [
            InlineQueryResultArticle(
                result["title"],
                InputTextMessageContent(
                    f'**__{result["title"]}__** [‎ ]({result["thumb"]})'
                ),
                reply_markup=ikb([
                    [(
                        'Assistir',
                        f'anime={result["id"]}&page=1'
                    )]
                ]),
                thumb_url=result['thumb']
            )
            for result in results['results']
        ]

        await q.answer(results, config.INLINE_CACHE, next_offset=offset)
    else:
        if page == 1:
            await q.answer(
                results=[],
                cache_time=config.INLINE_CACHE,
                switch_pm_text=f'Sem resultados para "{query}"',
                switch_pm_parameter='no_results',
            )
        else:
            await q.answer(
                results=[],
                cache_time=config.INLINE_CACHE,
                next_offset=''
            )
