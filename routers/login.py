from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from security import verificar_senha, criar_token_acesso
from database import get_db
from pydantic import BaseModel

# 1. Definimos exatamente o que o frontend vai enviar no JSON
class LoginDados(BaseModel):
    email: str
    senha: str

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginDados, db = Depends(get_db)):
    # Busca o funcionário pelo e-mail
    query = text("""
        SELECT id, empresa_id, senha_hash, nome, cargo 
        FROM public.funcionario 
        WHERE email = :email AND ativo = TRUE;
    """)
    result = db.execute(query, {"email": dados_login.email.strip()})
    funcionario = result.fetchone()

    # Se não encontrar o e-mail no banco, já barra aqui com 401
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    # Mapeia as colunas retornadas pelo banco de dados
    dados_banco = funcionario._mapping
    senha_hash = dados_banco["senha_hash"]

    # Valida se a senha digitada bate com o hash criptografado do banco
    if not verificar_senha(dados_login.senha, senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
        
    # O SEGREDO PARA NÃO TRAVAR: Convertemos os UUIDs explicitamente para texto (str)
    # Isso impede o "Internal Server Error" que travava a resposta do Python
    dados_do_token = {
        "sub": str(dados_banco["id"]),
        "empresa_id": str(dados_banco["empresa_id"]),
        "cargo": str(dados_banco["cargo"])
    }
    
    # Gera o Token de acesso seguro
    token = criar_token_acesso(dados_do_token)
    
    # Retorna a resposta perfeita que o React precisa ler
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "nome": str(dados_banco["nome"]),
            "cargo": str(dados_banco["cargo"])
        }
    }