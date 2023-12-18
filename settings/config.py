import configparser
import json

from .settings import BASE_DIR


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(f'{BASE_DIR}/config.ini', encoding='utf-8-sig')
    return config


def get_proxies() -> dict:
    with open(f'{BASE_DIR}/proxies.json', encoding='utf-8-sig') as proxies:
        proxies_json = json.load(proxies)
    return proxies_json