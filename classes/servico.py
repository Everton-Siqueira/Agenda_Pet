from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

class Servico(BaseModel):
    
    tipo_servico: str = Field(..., 
    min_length=3,
    max_length=20,
    description="Tipo do serviço")

    valor: Decimal = Field(..., 
    gt=0,
    decimal_places=2,
    description="Valor do serviço")
    
    @field_validator('tipo_servico')
    def validar_tipo_servico(cls, servico):
        servico = servico.strip()
        servico = " ".join(servico.split())

        if not servico:
            raise ValueError("O tipo de serviço não pode ser vazio.")
        for caracter in servico:
            if caracter.isnumeric():
                raise ValueError("O tipo de serviço não pode conter números.")
        return servico



    