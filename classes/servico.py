from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

class Servico(BaseModel):
    nome_servico: str = Field(
        ..., 
        min_length=3,
        max_length=20,
        description="Nome do serviço"
    )

    preco: float = Field(
        ..., 
        gt=0,
        decimal_places=2,
        description="Preço do serviço"
    )
    
    @field_validator('nome_servico')
    def validar_nome_servico(cls, servico: str) -> str:
        # Remove espaços nas pontas e reduz múltiplos espaços internos a um só
        servico = " ".join(servico.strip().split())

        if not servico:
            raise ValueError("O nome do serviço não pode estar vazio.")

        # Bloqueia números no nome do serviço
        if any(caracter.isnumeric() for caracter in servico):
            raise ValueError("O nome do serviço não pode conter números.")

        palavras_minusculas = ["de", "da", "do", "das", "dos"]
        palavras = servico.split()
        resultado = []

        for palavra in palavras:
            # Comparamos em minúsculo (.lower()) para não escapar nenhuma preposição maiúscula
            if palavra.lower() in palavras_minusculas:
                resultado.append(palavra.lower())
            else:
                resultado.append(palavra.title())

        return " ".join(resultado)
    