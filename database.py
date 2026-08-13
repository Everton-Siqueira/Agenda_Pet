import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

with open('ddl.sql') as arquivo:
    createSQL = arquivo.read()

with open('dml.sql', encoding='utf8') as arquivo:
    insertSQL = arquivo.read()

engine = create_engine(DATABASE_URL)
with engine.begin() as con:
    con.execute(text(createSQL))
    con.execute(text(insertSQL))
    engine.dispose()
