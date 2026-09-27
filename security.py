import jwt
from datetime import datetime, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Diz ao FastAPI onde o token deve ser enviado (geralmente via Header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ... mantenha suas funções anteriores (gerar_senha_hash, verificar_senha, criar_token_acesso) ...

def obter_usuario_logado(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodifica o JWT, valida a expiração e retorna os dados do funcionário.
    Se o token estiver quebrado ou expirado, bloqueia o acesso imediatamente.
    """
    credenciais_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Acesso negado. Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o token usando a sua chave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        funcionario_id: str = payload.get("sub")
        empresa_id: str = payload.get("empresa_id")
        cargo: str = payload.get("cargo")
        
        if funcionario_id is None or empresa_id is None:
            raise credenciais_exception
            
        # Retorna um dicionário com os dados limpos para a rota usar
        return {
            "funcionario_id": funcionario_id,
            "empresa_id": empresa_id,
            "cargo": cargo
        }
        
    except jwt.PyJWTError:
        raise credenciais_exception