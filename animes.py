import httpx
import re

from urllib.parse import quote
from bs4 import BeautifulSoup

session = httpx.AsyncClient(verify=False, timeout=15)
default_headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Sec-GPC': '1',
    'Accept-Language': 'pt-BR,pt;q=0.8',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document'
}


async def search_anime(query: str, page=1):
    headers = default_headers
    headers['Referer'] = 'https://animesdigital.org/'
    req = await session.get(
        f'https://animesdigital.org/page/{page}/?s={quote(query)}',
        headers=headers
    )
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, 'html.parser')
        results = soup.find_all(class_='itemA')
        if results:
            animes = {
                'results': [],
                'max_pages': 1
            }
            for result in results:
                anime = result.find('a')
                path = re.search(r'^https://animesdigital\.org/anime/a/(.+)$', anime.get('href'), re.M).group(1)
                thumb = anime.find(class_='thumb').find('img')['src']
                title = anime.find(class_='title').find(class_='title_anime').text.strip()
                animes['results'].append({
                    'path': path,
                    'thumb': thumb,
                    'title': title
                })

            nav = soup.find(class_='content-pagination')
            if nav:
                items = nav.find_all('li')
                max_pages = 0
                for li in items:
                    n = li.find('span') or li.find('a')
                    if n and n.text.isdigit():
                        max_pages = max(max_pages, int(n.text))
                max_pages = None if max_pages == 0 else max_pages
                animes['max_pages'] = max_pages

            return animes


async def get_anime(path: str, page=1):
    req = await session.get(
        f'https://animesdigital.org/anime/a/{path}/page/{page}/?odr=1',
        headers=default_headers,
        follow_redirects=True
    )
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, 'html.parser')

        anime = {
            'episodes': [],
            'max_pages': 1,
            'thumb': soup.find(class_='poster').find('img')['src'],
            'title': soup.find(class_='dados').find('h1').text.strip(),
            'desc': soup.find(class_='sinopse').text
        }

        eps = soup.find_all(class_='item_ep b_flex')
        if eps:
            for ep in eps:
                a = ep.find('a')
                post_id = re.search(r'^https://animesdigital.org/video/a/(.+)/$', a.get('href'), re.M).group(1)
                title = a.find(class_='episode').text
                ep_num = re.search(r'\d+(\.\d+)?', title)
                if ep_num:
                    title = ep_num.group()
                else:
                    title = a.find(class_='sub_title').text
                anime['episodes'].append({
                    'id': post_id,
                    'title': title
                })

        nav = soup.find(class_='content-pagination')
        if nav:
            items = nav.find_all('li')
            max_pages = 0
            for li in items:
                n = li.find('span') or li.find('a')
                if n and n.text.isdigit():
                    max_pages = max(max_pages, int(n.text))
            max_pages = None if max_pages == 0 else max_pages
            anime['max_pages'] = max_pages

        if anime['max_pages']:
            if page != anime['max_pages']:
                anime['episodes'] = [ep for ep in anime['episodes'] if not re.search(r'OVA', ep['title'], re.I)]

        return anime


async def get_episode(episode):
    req = await session.get(
        f'https://animesdigital.org/video/a/{episode}/',
        headers=default_headers
    )
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, 'html.parser')

        episode = {
            'title': soup.find('span', id='anime_title').text,
            'file': re.search(r"file: '(.+)'", req.text).group(1),
            'thumb': re.search(r"image: '(.+)'", req.text).group(1),
            'prev_episode': None,
            'next_episode': None
        }

        prev_episode = soup.find('a', class_='anteriorLink').get('href')
        next_episode = soup.find('a', class_='proximoLink').get('href')
        reg = re.search(r'^https://animesdigital.org/video/a/(.+)/$', prev_episode, re.M)
        reg2 = re.search(r'^https://animesdigital.org/video/a/(.+)/$', next_episode, re.M)
        if reg:
            if reg.group(1) != '#':
                episode['prev_episode'] = reg.group(1)
        if reg2:
            if reg2.group(1) != '#':
                episode['next_episode'] = reg2.group(1)

        return episode
