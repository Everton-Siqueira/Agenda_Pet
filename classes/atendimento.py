from pydantic import BaseModel, Field

class Atendimento(BaseModel):
    id_pet: int = Field(..., description="ID do pet atendido")
    data_atendimento: str = Field(..., description="Data do atendimento")
    descricao: str = Field(..., description="Descrição do atendimento")