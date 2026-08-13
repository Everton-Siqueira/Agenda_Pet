import os
from fastapi import APIRouter
from dotenv import load_dotenv
from classes.pet import Pet
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

router = APIRouter(prefix="/pet", tags=["Pet"])

engine = create_engine(DATABASE_URL)


@router.post("")
def create_pet(pet: Pet):
    try:
        with engine.connect() as conn:
            sql = """INSERT INTO pet (nome_pet, especie, id_tutor) 
                    VALUES (:nome_pet, :especie, :id_tutor)"""

            dados = {
                "nome_pet": pet.nome_pet,
                "especie": pet.especie,
                "id_tutor": pet.id_tutor
            }

            conn.execute(text(sql), dados)
            conn.commit()
    except Exception as e:
        return {"error": str(e)}          
    
   
    return {"message": "Pet criado com sucesso!"}

    