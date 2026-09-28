from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

class LoginDados(BaseModel):
    email: str
    senha: str

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginDados):
    # BYPASS DE TESTE: Ignora o banco temporariamente para validar PC e Celular
    email_digitado = dados_login.email.strip().lower()
    
    if email_digitado == "teste@pet.com" and dados_login.senha == "123":
        return {
            "access_token": "TOKEN_DE_TESTE_SUPER_SEGURO",
            "token_type": "bearer",
            "usuario": {
                "nome": "Funcionario Teste",
                "cargo": "Administrador"
            }
        }
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="E-mail ou senha incorretos de teste."
    )