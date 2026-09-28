from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from classes.login import LoginSchema
from security import verificar_senha, criar_token_acesso
from database import get_db

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginSchema, db = Depends(get_db)):
    # Busca o funcionário pelo e-mail
    query = text("SELECT id, empresa_id, senha_hash, nome, cargo FROM funcionario WHERE email = :email AND ativo = TRUE;")
    result = db.execute(query, {"email": dados_login.email})
    funcionario = result.fetchone()

    # 1º CORREÇÃO: Verifica se o funcionário existe ANTES de tentar mapear a senha_hash
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    # Agora sim é seguro ler o mapeamento
    senha_hash = funcionario._mapping["senha_hash"]

    # 2º CORREÇÃO: Compara as senhas com segurança
    if not verificar_senha(dados_login.senha, senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
        
    # Monta a carga (payload) do token JWT usando o mapeamento correto do record
    dados_do_token = {
        "sub": str(funcionario._mapping["id"]),
        "empresa_id": str(funcionario._mapping["empresa_id"]),
        "cargo": funcionario._mapping["cargo"]
    }
    
    token = criar_token_acesso(dados_do_token)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "nome": funcionario._mapping["nome"],
            "cargo": funcionario._mapping["cargo"]
        }
    }