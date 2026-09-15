import re
from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from decimal import Decimal

class Atendimento(BaseModel):
    id_pet: int = Field(...,
    gt= 0,
    le=999,
    description="ID do pet atendido")

    data_atendimento: date = Field(...,
    description="Data do atendimento")

    horario_atendimento: time = Field(...,
    description="Hora do atendimento")
    
    id_servico: int = Field(...,
    gt= 0,
    description="ID do serviço realizado")

    valor: Decimal = Field(...,
    gt=0,
    le=999.99,
    decimal_places=2,
    description="Valor do atendimento")

    @field_validator('horario_atendimento')
    def validar_horario_atendimento(cls, horario_atendimento):
        if horario_atendimento < time(9, 0) or horario_atendimento > time(18, 0):
            raise ValueError("O horário de atendimento deve estar entre 09:00 e 18:00.")
        return horario_atendimento

    @field_validator("data_atendimento", mode="before")
    def formatar_data_flexivel(cls, value):
        if isinstance(value, str):
            # 1. Remove qualquer caractere que não seja número (espaços, barras, hífens, pontos)
            apenas_numeros = re.sub(r"\D", "", value)

            # 2. Se a pessoa digitou 8 números (ex: "14092026")
            if len(apenas_numeros) == 8:
                dia = apenas_numeros[0:2]
                mes = apenas_numeros[2:4]
                ano = apenas_numeros[4:8]
                return f"{ano}-{mes}-{dia}"

        return value
        