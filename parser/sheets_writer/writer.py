import asyncio
import csv
from typing import NamedTuple

import aiocsv
import aiofiles
import gspread
from configparser import ConfigParser


class Writer:
    def __init__(self, config: ConfigParser):
        self.config = config
        self.gsp = self._get_gsp()

    def create_table(self):
        with open('data.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['Название компании', 'URL вакансии', 'URL компании', 'Профиль на LinkedIn', 'Присутствующие тэги'])

    def write_lines(self, lines: list):
        with open('data.csv', 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=',') #Изменить делимитер
            writer.writerows(lines)

    async def write_line(self, line):
        async with aiofiles.open('data.csv', 'a', encoding='utf-8-sig', newline='') as f:
            writer = aiocsv.AsyncWriter(f, delimiter=';')
            await writer.writerow(line)

    def _get_gsp(self) -> gspread.Client:
        gsp = gspread.oauth(credentials_filename='credentials/credentials.json', authorized_user_filename='credentials/auth.json')
        return gsp

    def _get_spreadsheet(self) -> gspread.Spreadsheet:
        try:
            sh = self.gsp.open(self.config.get('parser', 'table'))
        except gspread.exceptions.SpreadsheetNotFound:
            sh = self.gsp.create(self.config.get('parser', 'table'))
        return sh

    def gsp_writer(self):
        sh = self._get_spreadsheet()
        content = open('data.csv', 'r', encoding='utf-8-sig').read()
        self.gsp.import_csv(sh.id, content)