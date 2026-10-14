from fastapi import APIRouter, HTTPException, status, Depends
from classes.pet import Pet
from sqlalchemy import text
from database import engine
from security import obter_usuario_logado # Importa a nossa trava de segurança

router = APIRouter(prefix="/pet", tags=["Pet"])

@router.post("")
def create_pet(pet: Pet, usuario: dict = Depends(obter_usuario_logado)):
    try:
        with engine.begin() as conn:
            # Incluído 'empresa_id' no INSERT para amarrar o pet à clínica certa
            sql = """INSERT INTO pet (nome_pet, especie, id_tutor, empresa_id) 
                    VALUES (:nome_pet, :especie, :id_tutor, :empresa_id)
                    RETURNING id"""
                    
            dados = {
                "nome_pet": pet.nome_pet,
                "especie": pet.especie,
                "id_tutor": pet.id_tutor,
                "empresa_id": usuario["empresa_id"] # Extraído direto do Token JWT de forma segura
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
def get_pets(usuario: dict = Depends(obter_usuario_logado)):
    try:
        with engine.connect() as conn:
            # Filtrando o SELECT para trazer APENAS os pets pertencentes a esta empresa_id
            sql = """SELECT * FROM pet WHERE empresa_id = :empresa_id"""
            result = conn.execute(text(sql), {"empresa_id": usuario["empresa_id"]})
            pets = [dict(row._mapping) for row in result]
            return pets

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pets: {str(e)}",
        )

@router.get("/{pet_id}")
def get_pet(pet_id: int, usuario: dict = Depends(obter_usuario_logado)):   
    try:
        with engine.connect() as conn:
            # Segurança extra: impede que funcionário de outra clínica adivinhe o id do pet na URL
            sql = """SELECT * FROM pet WHERE id = :pet_id AND empresa_id = :empresa_id"""
            result = conn.execute(text(sql), {
                "pet_id": pet_id,
                "empresa_id": usuario["empresa_id"]
            })
            pet = result.fetchone()
            
            if pet:
                return dict(pet._mapping)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pet não encontrado ou sem permissão de acesso."
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pet: {str(e)}",
        )

    

@router.put("/{pet_id}")
def update_pet(pet_id: int, pet: Pet, usuario: dict = Depends(obter_usuario_logado)):  
    try:
        with engine.begin() as conn:
            # Trava adicionada no WHERE do UPDATE para só editar se pertencer à empresa
            sql = """UPDATE pet SET nome_pet = :nome_pet, especie = :especie, id_tutor = :id_tutor 
                    WHERE id = :pet_id AND empresa_id = :empresa_id"""

            dados = {
                "nome_pet": pet.nome_pet,
                "especie": pet.especie,
                "id_tutor": pet.id_tutor,
                "pet_id": pet_id,
                "empresa_id": usuario["empresa_id"]
            }

            result = conn.execute(text(sql), dados)
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pet não encontrado ou sem permissão para atualizar.",
                )

            return {"message": "Pet updated successfully!"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar pet: {str(e)}",
        )


@router.delete("/{pet_id}")
def delete_pet(pet_id: int, usuario: dict = Depends(obter_usuario_logado)):    
    try:
        with engine.begin() as conn:
            # Trava adicionada no WHERE do DELETE para só apagar se for da mesma empresa
            sql = """DELETE FROM pet WHERE id = :pet_id AND empresa_id = :empresa_id"""
            result = conn.execute(text(sql), {
                "pet_id": pet_id, 
                "empresa_id": usuario["empresa_id"]
            })
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pet não encontrado ou sem permissão para deletar.",
                )
            return {"message": "Pet deletado com sucesso!"}

    except HTTPException:
        raise
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar pet: {str(e)}",
        )