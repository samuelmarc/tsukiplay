import json
import io
import asyncio

from pyromod import ikb
from pyromod.exceptions import ListenerTimeout

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from database import database
from config import config


@Client.on_message(filters.command('start'))
async def start(_, m: Message):
    conn = database.conn
    async with conn.cursor() as cur:
        user_id = m.from_user.id
        await cur.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        user = await cur.fetchone()
        if not user:
            await cur.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            await conn.commit()
    await m.reply(
        f'''
        Olá, {m.from_user.mention}

Bem vindo ao **TsukiPlay**, aqui você poderá assistir a animes diretamente no telegram de forma fácil e prática e **sem anúncios!**

__Developed by @brabbit_ks__
        ''',
        reply_markup=ikb([
            [('Pesquisar Animes', '', 'switch_inline_query_current_chat')]
        ])
    )


@Client.on_message(filters.command('ex') & filters.user(config.SUDO_USERS))
async def ex_db(_, m: Message):
    conn = database.conn
    async with conn.cursor() as cur:
        query = ' '.join(m.command[1:])
        try:
            await cur.execute(query)
            data = await cur.fetchall()
            await conn.commit()
            rows_affected = cur.rowcount
            rows = await m.reply(f'📶 Affected Rows: {rows_affected}', True)
            if data:
                data = json.dumps(
                    [
                        dict(row) for row in data
                    ],
                    indent=2
                )
                try:
                    await rows.reply(f'<pre language="json">{data}</pre>', True)
                except MessageTooLong:
                    data = io.BytesIO(data.encode('utf-8'))
                    await rows.reply_document(data, True, file_name='result.json')
        except Exception as e:
            await m.reply(f'An error has occurred:\n\n<pre language="python">{e}</pre>')


@Client.on_message(filters.command('notify') & filters.user(config.SUDO_USERS))
async def notify_users(cl: Client, m: Message):
    try:
        msg_ask = await m.from_user.ask(
            'Envie a mensagem para transmitir: ',
            timeout=60
        )
    except ListenerTimeout:
        return await m.reply('Tempo pra enviar a mensagem esgotado.')

    while True:
        try:
            confirm_ask = await m.from_user.ask(
                'Você confirma? (S/N)',
                filters=filters.text,
                timeout=60
            )
        except ListenerTimeout:
            return await m.reply('Tempo pra confirmar esgotado.')
        confirm_ask = confirm_ask.text
        if confirm_ask.lower() not in ['s', 'n']:
            await m.reply('Por favor confirme utilizando S (Sim) ou N (Não)')
            continue

        if confirm_ask.lower() == 'n':
            await m.reply('Ok, operação cancelada.')
            return

        break

    async with database.conn.cursor() as cur:
        await cur.execute('SELECT user_id FROM users')
        users = await cur.fetchall()

        no_users = 'Não foram encontrados usuários registrados.'
        if not users:
            return await m.reply(no_users)
        users = [user for user in users if user['user_id'] not in config.SUDO_USERS]
        if not users:
            return await m.reply(no_users)

    progress = await m.reply('Enviando mensagens...')

    ok = 0
    fail = 0
    total_users = len(users)

    for index, user in enumerate(users, start=1):
        try:
            await cl.copy_message(
                user['user_id'],
                m.chat.id,
                msg_ask.id,
                msg_ask.caption
            )
            ok += 1
        except:
            fail += 1

        percentage = (index / total_users) * 100
        await progress.edit(f'Enviando mensagens...\nProgresso: {int(percentage)}% ({ok} enviadas, {fail} falhadas)\nTotal de usuários: {total_users}')

        await asyncio.sleep(3)
