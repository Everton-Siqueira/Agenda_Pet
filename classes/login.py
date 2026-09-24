from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
    senha: str
    id_empresa: int 

    senha: str = Field(..., description="Senha do usuário")

    @field_validator('senha')
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
         
