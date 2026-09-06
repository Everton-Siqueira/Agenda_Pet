from pydantic import BaseModel, Field

class Dashboard(BaseModel):
    total_pets: int = Field(..., description="Total de pets cadastrados")
    total_servicos: int = Field(..., description="Total de serviços cadastrados")
    total_atendimentos: int = Field(..., description="Total de atendimentos realizados")
