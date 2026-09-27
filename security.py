from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt  # Importa a biblioteca PyJWT instalada

# CONFIGURAÇÕES DE SEGURANÇA (Mantenha segredo em produção!)
SECRET_KEY = "sua_chave_secreta_super_dificil_e_longa_aqui" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 # O token expira em 8 horas (um turno de trabalho)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_senha_hash(senha_plana: str) -> str:
    return pwd_context.hash(senha_plana)

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)

# --- NOVA FUNÇÃO ABAIXO ---
def criar_token_acesso(dados: dict) -> str:
    """Gera o Token JWT contendo as informações do funcionário e empresa."""
    dados_para_criptografar = dados.copy()
    
    # Define o tempo de expiração do token usando fuso horário UTC (padrão recomendado em 2026)
    tempo_expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # O campo 'exp' é o padrão do JWT para checar validade automaticamente
    dados_para_criptografar.update({"exp": tempo_expiracao})
    
    # Cria e assina o Token
    token_jwt = jwt.encode(dados_para_criptografar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt