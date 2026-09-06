from fastapi import APIRouter, HTTPException, status
from classes.pet import Pet
from sqlalchemy import text
from database import engine

router = APIRouter(prefix="/pet", tags=["Pet"])

@router.post("")
def create_pet(pet: Pet):
    try:
        with engine.begin() as conn:
            sql = """INSERT INTO pet (nome_pet, especie, id_tutor) 
                    VALUES (:nome_pet, :especie, :id_tutor)
                    RETURNING id"""
                    
            dados = {
                "nome_pet": pet.nome_pet,
                "especie": pet.especie,
                "id_tutor": pet.id_tutor
            }
            result = conn.execute(text(sql), dados)
            pet_id = result.fetchone()[0]
            
            return {"message": "Pet criado com sucesso!", "id": pet_id}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar pet: {str(e)}",
        )

    
@router.get("")
def get_pets():
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM pet"""
            result = conn.execute(text(sql))
            pets = [dict(row._mapping) for row in result]
            return pets

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pets: {str(e)}",
        )

@router.get("/{pet_id}")
def get_pet(pet_id: int):   
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM pet WHERE id = :pet_id"""
            result = conn.execute(text(sql), {"pet_id": pet_id})
            pet = result.fetchone()
            
            if pet:
                return dict(pet._mapping)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pet não encontrado"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pet: {str(e)}",
        )

    

@router.put("/{pet_id}")
def update_pet(pet_id: int, pet: Pet):  
    try:
        with engine.begin() as conn:
            sql = """UPDATE pet SET nome_pet = :nome_pet, especie = :especie, id_tutor = :id_tutor 
                    WHERE id = :pet_id"""

            dados = {
                "nome_pet": pet.nome_pet,
                "especie": pet.especie,
                "id_tutor": pet.id_tutor,
                "pet_id": pet_id
            }

            result = conn.execute(text(sql), dados)
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pet não encontrado",
                )


            return {"message": "Pet atualizado com sucesso!"}




    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar pet: {str(e)}",
        )


@router.delete("/{pet_id}")
def delete_pet(pet_id: int):    
    try:
        with engine.begin() as conn:
            sql = """DELETE FROM pet WHERE id = :pet_id"""
            result = conn.execute(text(sql), {"pet_id": pet_id})
            

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pet não encontrado",
                )
            return {"message": "Pet deletado com sucesso!"}

    except HTTPException:
        raise
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar pet: {str(e)}",
        )

       
    