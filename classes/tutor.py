from pydantic import BaseModel, Field

class Tutor(BaseModel):
    
    nome: str = Field(..., description="Nome do tutor")
    endereco: str = Field(..., description="Endereço do tutor")
    celular: str = Field(..., description="Celular do tutor")