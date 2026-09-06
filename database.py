import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega a variável DATABASE_URL do .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "A variável DATABASE_URL não foi encontrada no arquivo .env!"
    )

# Cria o pool de conexões reutilizável para a aplicação
engine = create_engine(DATABASE_URL)


def testar_conexao():
    """Apenas testa se o banco de dados do pgAdmin está acessível."""
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        print("Conexão com o PostgreSQL realizada com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")


# Executa o teste de conexão apenas ao rodar "python database.py" diretamente
if __name__ == "__main__":
    testar_conexao()