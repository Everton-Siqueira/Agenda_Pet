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
    # Busca o funcionário pelo e-mail
    query = text("SELECT id, empresa_id, senha_hash, nome, cargo FROM funcionario WHERE email = :email AND ativo = TRUE;")
    result = db.execute(query, {"email": dados_login.email})
    funcionario = result.fetchone()

    # 1. Validação se o usuário existe
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    # 2. Validação da Senha acessando os atributos de forma segura e universal
    senha_hash = funcionario.senha_hash
    if not verificar_senha(dados_login.senha, senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
        
    # 3. Monta a carga (payload) do token JWT usando os atributos diretos do objeto mapeado
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