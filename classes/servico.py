from pydantic import BaseModel, Field

class Servico(BaseModel):
    
    tipo_servico: str = Field(..., 
    min_length=3,
    max_length=20,
    description="Tipo do serviço")

    valor: float = Field(..., 
    gt=0,
    description="Valor do serviço")
    