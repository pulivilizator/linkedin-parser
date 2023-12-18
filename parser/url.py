from settings import settings, config
import random

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from configparser import ConfigParser
from math import ceil

def _get_count_vacancies(query: dict) -> int:
    proxies = random.choice(config.get_proxies())
    proxy = {'https': f'socks5://{proxies["username"]}:{proxies["password"]}@{proxies["server"]}:{proxies["port"]}'}
    ua = UserAgent()
    response = requests.get(url=settings.GET_PAGES_COUNT_URL.format(query['keywords'],
                                                                    query['location']),
                            headers={'user-agent': ua.random},
                            proxies=proxy)

    soup = BeautifulSoup(response.text, 'html.parser')
    vacancies = soup.find('span', class_='results-context-header__job-count').text
    return int(vacancies.replace(',', '').replace('+', ''))

def get_pages_urls(config: ConfigParser) -> list[str]:
    query = {
        'keywords': config.get('parser', 'keywords'),
        'location': config.get('parser', 'location')
    }

    vacancies_count = _get_count_vacancies(query=query)
    if vacancies_count > config.getint('parser', 'vacs_limiter'):
        vacancies_count = config.getint('parser', 'vacs_limiter')

    pages_count = ceil(vacancies_count / 25)

    urls = [
        settings.VACANCIES_URL.format(query['keywords'], query['location'], page * 25)
        for page in range(pages_count)
    ]
    return urls

