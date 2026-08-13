from pydantic import BaseModel, Field

class Servico(BaseModel):
    
    tipo_servico: str = Field(..., description="Tipo do serviço")
    valor: float = Field(..., description="Valor do serviço")
    