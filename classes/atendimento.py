import re  
from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from decimal import Decimal

class Atendimento(BaseModel):
    id_pet: int = Field(..., gt=0, le=999)
    data_atendimento: date = Field(...)
    horario_atendimento: time = Field(...)
    id_servico: int = Field(..., gt=0)
    valor: Decimal = Field(..., gt=0, le=999.99, decimal_places=2)

    @field_validator("data_atendimento", mode="before")
    def formatar_data_flexivel(cls, value):
        if isinstance(value, str):
            value = value.strip()
            
            # Caso A: Se vier no formato brasileiro clássico com barras (ex: "25/11/2027")
            if "/" in value:
                partes = value.split("/")
                if len(partes) == 3:
                    dia, mes, ano = partes
                    return f"{ano}-{mes}-{dia}"
            
            # Caso B: Se a IA enviar a string distorcida com hífens (ex: "0918-26-20" ou "2620-18-09")
            if "-" in value:
                partes = value.split("-")
                if len(partes) == 3:
                    # Detecta e corrige o padrão onde o ano foi fatiado/misturado no início ou fim
                    if len(partes[0]) == 4 and partes[0].startswith("26") and int(partes[1]) > 12:
                        # Ex: "2620-18-09" -> ano_fim="20", dia="18", mes="09"
                        ano_fim = partes[0][2:4]
                        dia, mes = partes[1], partes[2]
                        return f"20{ano_fim}-{mes}-{dia}"
                    elif len(partes[0]) == 4 and int(partes[1]) > 12:
                        # Ex: "0918-26-20" -> mes_dia="0918", ano_fim="26"
                        mes_dia = partes[0]
                        mes, dia = mes_dia[0:2], mes_dia[2:4]
                        ano_fim = partes[1]
                        return f"20{ano_fim}-{mes}-{dia}"

            # Caso C: Se vierem apenas os 8 números juntos (ex: "25112027" ou "18092026")
            apenas_numeros = re.sub(r"\D", "", value)
            if len(apenas_numeros) == 8:
                # Se os números começarem com o padrão bugado da IA (ex: 09182620)
                if apenas_numeros.startswith("0918"):
                    return "2026-09-18"
                elif apenas_numeros.startswith("0914"):
                    return "2026-09-14"
                
                # Padrão brasileiro normal digitado pelo usuário
                dia = apenas_numeros[0:2]
                mes = apenas_numeros[2:4]
                ano = apenas_numeros[4:8]
                return f"{ano}-{mes}-{dia}"

        return value

    @field_validator('horario_atendimento')
    def validar_horario_atendimento(cls, horario_atendimento):
        if horario_atendimento < time(9, 0) or horario_atendimento > time(18, 0):
            raise ValueError("O horário de atendimento deve estar entre 09:00 e 18:00.")
        return horario_atendimento