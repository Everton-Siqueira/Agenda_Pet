from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from classes.login import LoginSchema
from security import verificar_senha, criar_token_acesso
from database import get_db

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginSchema, db = Depends(get_db)):
    # Busca o funcionário pelo e-mail
    query = text("SELECT id, empresa_id, senha_hash, nome, cargo FROM funcionarios WHERE email = :email AND ativo = TRUE;")
    result = db.execute(query, {"email": dados_login.email})
    funcionario = result.fetchone()
    
    # Se não encontrar ou a senha estiver errada, barra o acesso
    # (.senha_hash e .nome funcionam mapeados pelo mapeamento de colunas do SQLAlchemy)
    if not funcionario or not verificar_senha(dados_login.senha, funcionario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
        
    # Monta a carga (payload) do token JWT
    dados_do_token = {
        "sub": str(funcionario.id),
        "empresa_id": str(funcionario.empresa_id),
        "cargo": funcionario.cargo
    }
    
    token = criar_token_acesso(dados_do_token)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "nome": funcionario.nome,
            "cargo": funcionario.cargo
        }
    }