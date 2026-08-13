import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Conectando...")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        resultado = conn.execute(text("SELECT 1"))
        print(resultado.scalar())
        print("Conexão funcionando!")

except Exception as e:
    print("ERRO:")
    print(repr(e))