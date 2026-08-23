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
            raise ValueError("O tipo de serviço não pode estar vazio.")

        for caracter in servico:
            if caracter.isnumeric():
                raise ValueError("O tipo de serviço não pode conter números.")

        palavras_minusculas = ["de", "da", "do", "das", "dos"]
        palavras = servico.split()

        resultado = []

        for palavra in palavras:
            if palavra in palavras_minusculas:
                resultado.append(palavra)

            else:
                resultado.append(palavra.title())

        servico = " ".join(resultado)

        return servico

    