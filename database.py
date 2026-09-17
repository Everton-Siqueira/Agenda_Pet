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
    """Apenas testa se o banco de dados do pgAdmin está acessível e atualiza a estrutura."""
    try:
        with engine.connect() as con:
            # 1. Mantém o seu teste original de conexão
            con.execute(text("SELECT 1"))
            print("Conexão com o PostgreSQL realizada com sucesso!")
            
            # 2. Executa a criação da coluna de forma direta (sem o con.begin())
            con.execute(text("""
                ALTER TABLE atendimentos 
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pendente' NOT NULL;
            """))
            print("Estrutura da tabela atualizada: Coluna 'status' pronta!")
            
    except Exception as e:
        print(f"Erro ao conectar ou atualizar o banco de dados: {e}")

# Executa o teste de conexão apenas ao rodar "python database.py" diretamente
if __name__ == "__main__":
    testar_conexao()
