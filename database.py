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

def get_db():
    """Fornece uma conexão limpa do banco de dados para cada requisição do FastAPI."""
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()

def testar_conexao():
    """Testa a acessibilidade do PostgreSQL e garante as dependências do Multi-Tenant."""
    try:
        with engine.begin() as con:
            # 1. Teste de ping básico no banco
            con.execute(text("SELECT 1"))
            print("Conexão com o PostgreSQL realizada com sucesso!")
            
            print("Verificando e atualizando dependências estruturais do Multi-Tenant...")
            
            # 2. Garante que a tabela base de empresa exista
            con.execute(text("""
                CREATE TABLE IF NOT EXISTS public.empresa (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    cnpj VARCHAR(20) UNIQUE
                );
            """))

            # 3. Adiciona a coluna empresa_id nas tabelas existentes caso não existam
            # O bloco condicional impede erros caso a coluna já tenha sido criada antes
            tabelas_dependentes = ["funcionario", "tutor", "pet", "servico", "atendimento"]
            
            for tabela in tabelas_dependentes:
                con.execute(text(f"""
                    DO $$ 
                    BEGIN 
                        IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='{tabela}') THEN
                            IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_schema='public' AND table_name='{tabela}' AND column_name='empresa_id') THEN
                                ALTER TABLE public.{tabela} ADD COLUMN empresa_id INTEGER REFERENCES public.empresa(id) ON DELETE CASCADE;
                                RAISE NOTICE 'Coluna empresa_id adicionada na tabela %', '{tabela}';
                            END IF;
                        END IF;
                    END $$;
                """))
                
            print("Estrutura de dependências do banco de dados verificada com sucesso!")
                        
    except Exception as e:
        print(f"Erro ao conectar ou atualizar o banco de dados: {e}")

# Executa o teste de conexão apenas ao rodar "python database.py" diretamente
if __name__ == "__main__":
    testar_conexao()