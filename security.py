from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "sua_chave_secreta_super_segura_aqui"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# VEJA SE ESTÁ EXATAMENTE COM ESSE NOME ABAIXO:
def gerar_senha_hash(senha_plana: str) -> str:
    """Transforma a senha em um texto criptografado e seguro para o banco."""
    # Garante que o texto seja convertido corretamente e limita o tamanho caso necessário
    senha_limpa = senha_plana[:72] 
    return pwd_context.hash(senha_limpa)

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Compara a senha que o usuário digitou com o hash salvo no banco."""
    senha_limpa = senha_plana[:72]
    return pwd_context.verify(senha_limpa, senha_hash)
    
def criar_token_acesso(dados: dict) -> str:
    """Gera o Token JWT contendo as informações do funcionário e empresa."""
    dados_para_criptografar = dados.copy()
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_para_criptografar.update({"exp": tempo_expiracao})
    return jwt.encode(dados_para_criptografar, SECRET_KEY, algorithm=ALGORITHM)

def obter_usuario_logado(token: str = Depends(oauth2_scheme)) -> dict:
    """Decodifica o JWT e valida o acesso do funcionário."""
    credenciais_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Acesso negado. Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        funcionario_id: str = payload.get("sub")
        empresa_id: str = payload.get("empresa_id")
        cargo: str = payload.get("cargo")
        
        if funcionario_id is None or empresa_id is None:
            raise credenciais_exception
            
        return {
            "funcionario_id": funcionario_id,
            "empresa_id": empresa_id,
            "cargo": cargo
        }
    except jwt.PyJWTError:
        raise credenciais_exception