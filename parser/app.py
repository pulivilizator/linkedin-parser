from configparser import ConfigParser

from .vacancies import main
from .sheets_writer.writer import Writer

async def app(config: ConfigParser):
    w = Writer(config)
    w.create_table()
    vacs = await main(config)
    w.write_lines(vacs)
    w.gsp_writer()