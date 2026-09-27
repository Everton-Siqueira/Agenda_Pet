from fastapi import APIRouter, HTTPException, status, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
from classes.login import LoginSchema
from security import verificar_senha, criar_token_acesso
from database import get_db

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginSchema, conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Busca o funcionário pelo e-mail
        query = "SELECT id, empresa_id, senha_hash, nome, cargo FROM funcionarios WHERE email = %s AND ativo = TRUE;"
        cursor.execute(query, (dados_login.email,))
        funcionario = cursor.fetchone()
        
        # Erro genérico de login impede ataques de força bruta que tentam adivinhar e-mails válidos
        if not funcionario or not verificar_senha(dados_login.senha, funcionario["senha_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos."
            )
            
        # Monta a carga (payload) do token com os dados que o back-end vai precisar conferir depois
        dados_do_token = {
            "sub": str(funcionario["id"]),
            "empresa_id": str(funcionario["empresa_id"]),
            "cargo": funcionario["cargo"]
        }
        
        token = criar_token_acesso(dados_do_token)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "nome": funcionario["nome"],
                "cargo": funcionario["cargo"]
            }
        }
    finally:
        cursor.close()