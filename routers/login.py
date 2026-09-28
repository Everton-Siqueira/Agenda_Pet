from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from security import verificar_senha, criar_token_acesso
from database import get_db
from pydantic import BaseModel
import traceback

class LoginDados(BaseModel):
    email: str
    senha: str

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginDados, db = Depends(get_db)):
    try:
        # 1. Busca o funcionário pelo e-mail
        query = text("""
            SELECT id, empresa_id, senha_hash, nome, cargo 
            FROM public.funcionario 
            WHERE email = :email AND ativo = TRUE;
        """)
        result = db.execute(query, {"email": dados_login.email.strip()})
        funcionario = result.fetchone()

        # Validação se o usuário existe
        if not funcionario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail não encontrado no banco de dados."
            )

        # 2. Extração segura dos dados retornados pelo banco
        # Usamos uma estratégia dupla para garantir leitura em qualquer versão do SQLAlchemy
        try:
            dados_banco = funcionario._mapping
            id_usuario = dados_banco["id"]
            empresa_id = dados_banco["empresa_id"]
            senha_hash = dados_banco["senha_hash"]
            nome_usuario = dados_banco["nome"]
            cargo_usuario = dados_banco["cargo"]
        except Exception:
            # Caso a versão do seu SQLAlchemy não aceite _mapping, lê por índice posicional
            id_usuario = funcionario[0]
            empresa_id = funcionario[1]
            senha_hash = funcionario[2]
            nome_usuario = funcionario[3]
            cargo_usuario = funcionario[4]

        # 3. Validação da Senha
        if not verificar_senha(dados_login.senha, senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha incorreta para este usuário."
            )
            
        # 4. Montagem do Token convertendo obrigatoriamente UUIDs em strings puras
        dados_do_token = {
            "sub": str(id_usuario),
            "empresa_id": str(empresa_id),
            "cargo": str(cargo_usuario)
        }
        
        token = criar_token_acesso(dados_do_token)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "nome": str(nome_usuario),
                "cargo": str(cargo_usuario)
            }
        }

    except HTTPException as http_err:
        # Mantém os erros intencionais de validação (E-mail/Senha errados)
        raise http_err
    except Exception as e:
        # CASO O PYTHON QUEBRE POR DENTRO: Ele captura a falha e envia o texto real pro celular ler!
        erro_detalhado = f"Erro Interno no Python: {str(e)} -> Linha do erro: {traceback.format_exc()}"
        print(erro_detalhado) # Printa no terminal do PC
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"O Python quebrou no banco de dados! Detalhe técnico: {str(e)}"
        )