def process_eps_nav(anime_id, page, max_pages):
    nav = []
    previous_page = page - 1
    next_page = page + 1

    previous_page_plus = page - 4
    if previous_page_plus >= 1:
        nav.append(['←←', f'anime={anime_id}&page={previous_page_plus}'])
    if previous_page >= 1:
        nav.append(['←', f'anime={anime_id}&page={previous_page}'])

    if next_page <= max_pages:
        nav.append(['→', f'anime={anime_id}&page={next_page}'])
    next_page_plus = page + 4
    if next_page_plus <= max_pages:
        nav.append(['→→', f'anime={anime_id}&page={next_page_plus}'])

    return nav


def process_ep_nav(next_episode, previous_episode, anime_id, back_page):
    nav = []
    if previous_episode:
        nav.append(['←', f'episode={previous_episode}&anime={anime_id}&back={back_page}'])
    if next_episode:
        nav.append(['→', f'episode={next_episode}&anime={anime_id}&back={back_page}'])
    return nav
