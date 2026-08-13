from pydantic import BaseModel, Field

class Pet(BaseModel):
    
    nome_pet: str = Field(..., description="Nome do pet")
    especie: str = Field(..., description="Espécie do pet")
    id_tutor: int = Field(..., description="ID do tutor do pet")
