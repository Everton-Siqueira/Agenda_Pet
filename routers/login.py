from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from security import verificar_senha, criar_token_acesso
from database import get_db
from pydantic import BaseModel

class LoginDados(BaseModel):
    email: str
    senha: str

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginDados, db = Depends(get_db)):
    # Busca o funcionário real pelo e-mail informado
    query = text("""
        SELECT id, empresa_id, senha_hash, nome, cargo 
        FROM public.funcionario 
        WHERE email = :email AND ativo = TRUE;
    """)
    result = db.execute(query, {"email": dados_login.email.strip()})
    funcionario = result.fetchone()

    # Validação do Usuário
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    # Mapeia com segurança
    dados_banco = funcionario._mapping
    senha_hash = dados_banco["senha_hash"]

    # Validação da Senha criptografada
    if not verificar_senha(dados_login.senha, senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
        
    # PROTEÇÃO CONTRA O TRAVAMENTO: Convertemos os UUIDs explicitamente para Texto puro (str)
    dados_do_token = {
        "sub": str(dados_banco["id"]),
        "empresa_id": str(dados_banco["empresa_id"]),
        "cargo": str(dados_banco["cargo"])
    }
    
    # Cria o JWT válido aceito pelas rotas da agenda
    token = criar_token_acesso(dados_do_token)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "nome": str(dados_banco["nome"]),
            "cargo": str(dados_banco["cargo"])
        }
    }