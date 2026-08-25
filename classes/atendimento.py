from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from decimal import Decimal

class Atendimento(BaseModel):
    id_pet: int = Field(...,
    gt= 0,
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
        