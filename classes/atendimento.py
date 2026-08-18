from pydantic import BaseModel, Field

class Atendimento(BaseModel):
    id_pet: int = Field(..., description="ID do pet atendido")
    data_atendimento: str = Field(..., description="Data do atendimento")
    horario_atendimento: str = Field(..., description="Hora do atendimento")
    id_servico: int = Field(..., description="ID do serviço realizado")
    valor: float = Field(..., description="Valor do atendimento")