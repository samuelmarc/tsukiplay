import asyncio

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, WebAppInfo
from pyrogram.errors import MessageNotModified, FloodWait

from pyromod import ikb, array_chunk

from database import database
from animes import get_anime, get_episode
from nav import process_ep_nav, process_eps_nav
from config import config
from base64 import b64encode


msg_wait = 'Aguarde...'
msg_wait_s = 'Aguarde {} segundos...'


@Client.on_callback_query(filters.regex(r'^nav_info$'))
async def nav_info(_, c: CallbackQuery):
    return await c.answer('Botão para visualização de páginas.')


@Client.on_callback_query(filters.regex(r'^anime=(\d+)&page=(\d+)$'))
async def anime_nav(_, c: CallbackQuery):
    anime_id = int(c.matches[0].group(1))

    async with database.conn.cursor() as cur:
        await cur.execute('SELECT alias FROM animes WHERE id = ?', (anime_id,))
        path = await cur.fetchone()
        if not path:
            return await c.answer('Não encontrei o anime no banco de dados, por favor tente pesquisar novamente.', True)
        path = path['alias']

    page = int(c.matches[0].group(2))
    anime = await get_anime(path, page)
    if anime and anime['episodes']:
        eps = [[ep['title'], f'episode={ep["id"]}&anime={anime_id}&back={page}'] for ep in anime['episodes']]
        eps = array_chunk(eps, 5)

        if anime['max_pages'] > 1:
            eps.append([(f'{page}/{anime["max_pages"]}', 'nav_info')])

        nav = process_eps_nav(anime_id, page, anime['max_pages'])
        if nav:
            eps.append(nav)

        eps = ikb(eps)

        try:
            await c.edit_message_text(
                f'**__{anime["title"]}__** [‎ ]({anime["thumb"]})\n\n>{anime["desc"]}',
                reply_markup=eps
            )
        except MessageNotModified:
            await c.answer(msg_wait)
        except FloodWait as e:
            await c.answer(msg_wait_s.format(e.value), True)
            await asyncio.sleep(e.value)
    else:
        await c.answer('Não consegui obter o anime, por favor tente novamente mais tarde.')


@Client.on_callback_query(filters.regex(r'^episode=(.+)&anime=(\d+)&back=(\d+)$'))
async def watch_episode(_, c: CallbackQuery):
    episode = c.matches[0].group(1)
    anime_id = int(c.matches[0].group(2))
    back_page = int(c.matches[0].group(3))
    episode = await get_episode(episode)
    if episode:
        web_url = config.WEB_APP + '?vid=' + b64encode(episode['file'].encode('utf-8')).decode('utf-8')
        btn = [
            [
                ('Assistir', WebAppInfo(url=web_url), 'web_app'),
                ('⌘', episode['file'], 'url')
            ]
        ]

        nav = process_ep_nav(episode['next_episode'], episode['prev_episode'], anime_id, back_page)
        if nav:
            btn.append(nav)
        btn.append([('Voltar', f'anime={anime_id}&page={back_page}')])
        btn = ikb(btn)

        try:
            await c.edit_message_text(
                f'**__{episode["title"]}__** [‎ ]({episode["thumb"]})',
                reply_markup=btn
            )
        except MessageNotModified:
            await c.answer(msg_wait)
        except FloodWait as e:
            await c.answer(msg_wait_s.format(e.value), True)
            await asyncio.sleep(e.value)
    else:
        await c.answer('Não foi possível obter o episódio, tente novamente mais tarde.')

