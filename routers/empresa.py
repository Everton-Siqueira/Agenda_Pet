from fastapi import APIRouter, HTTPException, status, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
from classes.empresa import CadastroEmpresaSchema
from security import gerar_senha_hash
from database import get_db # Supondo que sua conexão com o banco esteja centralizada em database.py

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])

@router.post("", status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(dados: CadastroEmpresaSchema, conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 1. Criação da Empresa no banco
        query_empresa = """
            INSERT INTO empresas (nome_comercial, razao_social, cnpj) 
            VALUES (%s, %s, %s) RETURNING id;
        """
        cursor.execute(query_empresa, (dados.nome_comercial, dados.razao_social, dados.cnpj))
        empresa_id = cursor.fetchone()["id"]
        
        # 2. Criptografia da senha do primeiro funcionário (Dono)
        senha_criptografada = gerar_senha_hash(dados.senha_dono)
        
        # 3. Criação do primeiro funcionário atrelado a essa empresa
        query_funcionario = """
            INSERT INTO funcionarios (empresa_id, nome, email, senha_hash, cargo) 
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query_funcionario, (
            empresa_id, dados.nome_dono, dados.email_dono, senha_criptografada, "admin"
        ))
        
        conn.commit()
        return {"mensagem": "Empresa e administrador criados com sucesso!", "empresa_id": empresa_id}
        
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O CNPJ informado ou o e-mail do administrador já estão cadastrados."
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()