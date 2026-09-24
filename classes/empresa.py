from pydantic import BaseModel, EmailStr

class Empresa(BaseModel):
    id: int
    nome_empresa: str
    endereco: str
    email: EmailStr
    