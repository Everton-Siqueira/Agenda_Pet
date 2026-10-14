from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class CadastroEmpresaSchema(BaseModel):
    # Dados da Empresa/Clínica Pet
    nome_comercial: str
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    
    # Dados do Primeiro Funcionário (O administrador/dono)
    nome_dono: str
    email_dono: EmailStr
    senha_dono: str = Field(..., description="Senha forte para o usuário administrador")

    # Sua lógica de validação rigorosa aplicada na criação da conta
    @field_validator('senha_dono')
    def validar_senha(cls, senha):
        if len(senha) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        if not any(char.isdigit() for char in senha):
            raise ValueError("A senha deve conter pelo menos um número.")
        if not any(char.isupper() for char in senha):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula.")
        if not any(char.islower() for char in senha):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula.")
        return senha