import asyncio
import time
from more_itertools import chunked
from aiohttp import ClientSession
from aiohttp_socks import ProxyType, ProxyConnector
from bs4 import BeautifulSoup
from configparser import ConfigParser
from fake_useragent import UserAgent
from itertools import chain

from .url import get_pages_urls
from .utils import *
from settings import settings, config as settings_config


async def get_soup(url: str, session: ClientSession) -> BeautifulSoup:
    await asyncio.sleep(2)
    ua = UserAgent()
    async with session.get(url, headers={'user-agent': ua.random}) as response:
        resp = await response.content.read()
        soup = BeautifulSoup(resp, 'html.parser')
    while '// Parse the tracking code from cookies.' in str(soup) or '"https://www.linkedin.com/authwall?trk="' in str(soup):
        async with session.get(url, headers={'user-agent': ua.random}) as response:
            resp = await response.content.read()
            soup = BeautifulSoup(resp, 'html.parser')
            await asyncio.sleep(5)
    return soup


async def get_vacancies(urls: list[str], proxy: dict) -> list[Urls]:
    vacancies = []
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5,
        host=proxy['server'],
        port=proxy['port'],
        username=proxy['username'],
        password=proxy['password'],
        rdns=True
    )
    async with ClientSession(connector=connector) as session:
        for url in urls:
            print(1)
            soup = await get_soup(url, session)
            vacs = soup.find_all('li')
            for i in vacs:
                el = i.find(class_='base-card')
                try:
                    urn = el['data-entity-urn'].split(':')[-1]
                    user_url = i.find('a')['href']
                    vacancies.append(Urls(user_url=user_url,
                                          dev_url=settings.SPECIFIC_VACANCY.format(urn, el['data-search-id'], el['data-tracking-id'])))
                except Exception as e:
                    print(e)
                    print(i)
                    print(url)
                    print(('get_vacancies'))
                    exit()

        return vacancies

async def get_company_site(name: str, session) -> str:
    soup = await get_soup(f'https://www.google.com/search?q={name.replace("&", " ")}', session)
    site = ''
    site_els = soup.find(id='search').find_all('a')
    for s in site_els:
        try:
            site = s['href']
        except KeyError:
            pass
        if site and 'http' in site and not any(w in s['href'] for w in settings.WRONG_WORDS):
            return site
    if not site:
        site = name

    return site

async def get_data(urls: list[Urls], proxy: dict, config: ConfigParser) -> list[Data]:
    datas = []
    config_tags = config.get('parser', 'tags').split()
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5,
        host=proxy['server'],
        port=proxy['port'],
        username=proxy['username'],
        password=proxy['password'],
        rdns=True
    )
    async with ClientSession(connector=connector) as session:
        for url in urls:
            soup = await get_soup(url.dev_url, session)
            linkedin_group_el = soup.find('a', class_='topcard__org-name-link')
            user_url = url.user_url
            tags = ', '.join([tag for tag in config_tags if tag.lower() in soup.text.lower()])
            if linkedin_group_el:
                linkedin_group = linkedin_group_el['href']
                name = linkedin_group_el.text.strip('\n ').replace('LLC', '')
                company_site = await get_company_site(name, session)
            else:
                try:
                    linkedin_group = soup.find('span', class_='topcard__flavor').text.strip('\n ')
                except Exception as e:
                    print(url)
                    print(e)
                company_site = await get_company_site(linkedin_group, session)
            d = Data(company_name=name,
                     vacancy_url=user_url,
                     tags=tags,
                     company_site=company_site,
                     linkedin_group=linkedin_group)
            datas.append(d)
            print(d)
    return datas

async def main(config: ConfigParser) -> list[list[str]]:
    datas_lists = []
    proxies = settings_config.get_proxies()
    url_list = split_list(get_pages_urls(config), len(proxies))
    vacs = await asyncio.gather(
                                *[asyncio.create_task(get_vacancies(urls, proxies[ind]))
                                  for ind, urls in enumerate(url_list)]
    )
    vacancies_urls = list(chunked(chain.from_iterable(vacs), 100))
    for vacancies_urls_p in vacancies_urls:
        vacancies_urls_tmp = split_list(vacancies_urls_p, len(proxies))
        datas_lists_tmp = await asyncio.gather(
                                    *[asyncio.create_task(get_data(urls, proxies[ind], config))
                                      for ind, urls in enumerate(vacancies_urls_tmp)]
        )
        datas_lists.extend(list(chain.from_iterable(datas_lists_tmp)))
        await asyncio.sleep(5)
    datas = [list(data) for data in datas_lists]
    return datas


