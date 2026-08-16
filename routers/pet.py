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

@router.get("")
def get_pets():
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM pet"""
            result = conn.execute(text(sql))
            pets = [dict(row._mapping) for row in result]
            return pets
    except Exception as e:
        return {"error": str(e)}
    
    return {"message": "Pets listados com sucesso!"}

@router.get("/{pet_id}")
def get_pet(pet_id: int):   
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM pet WHERE id_pet = :pet_id"""
            result = conn.execute(text(sql), {"pet_id": pet_id})
            pet = result.fetchone()
            if pet:
                return dict(pet)
            else:
                return {"message": "Pet não encontrado"}
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Pet listado com sucesso!"}

@router.put("/{pet_id}")
def update_pet(pet_id: int, pet: Pet):  
    try:
        with engine.connect() as conn:
            sql = """UPDATE pet SET nome_pet = :nome_pet, especie = :especie, id_tutor = :id_tutor 
                    WHERE id_pet = :pet_id"""

            dados = {
                "nome_pet": pet.nome_pet,
                "especie": pet.especie,
                "id_tutor": pet.id_tutor,
                "pet_id": pet_id
            }

            result = conn.execute(text(sql), dados)
            conn.commit()

            if result.rowcount == 0:
                return {"message": "Pet não encontrado"}
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Pet atualizado com sucesso!"}

@router.delete("/{pet_id}")
def delete_pet(pet_id: int):    
    try:
        with engine.connect() as conn:
            sql = """DELETE FROM pet WHERE id_pet = :pet_id"""
            result = conn.execute(text(sql), {"pet_id": pet_id})
            conn.commit()

            if result.rowcount == 0:
                return {"message": "Pet não encontrado"}
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Pet deletado com sucesso!"}    
    