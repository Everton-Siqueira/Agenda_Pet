from classes.tutor import Tutor
from database import engine
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

router = APIRouter(prefix="/tutor", tags=["Tutor"])


@router.post("")
def create_tutor(tutor: Tutor):
    try:
        with engine.begin() as conn:
            # RETURNING id permite resgatar a chave primária criada pelo PostgreSQL
            sql = """INSERT INTO tutor (nome, celular, endereco) 
                    VALUES (:nome, :celular, :endereco)
                    RETURNING id"""

            dados = {
                "nome": tutor.nome,
                "celular": tutor.celular,
                "endereco": tutor.endereco,
            }

            result = conn.execute(text(sql), dados)
            tutor_id = result.fetchone()[0]

            return {
                "message": "Tutor criado com sucesso!",
                "id": tutor_id,
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tutor: {str(e)}",
        )


@router.get("")
def get_tutores():
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM tutor"""
            result = conn.execute(text(sql))
            tutores = [dict(row._mapping) for row in result]
            return tutores

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tutores: {str(e)}",
        )


@router.get("/{tutor_id}")
def get_tutor(tutor_id: int):
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM tutor WHERE id = :tutor_id"""
            result = conn.execute(text(sql), {"tutor_id": tutor_id})
            tutor = result.fetchone()

            if tutor:
                return dict(tutor._mapping)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tutor não encontrado",
                )

    # Garante que o erro 404 passe direto para o FastAPI
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tutor: {str(e)}",
        )


@router.put("/{tutor_id}")
def update_tutor(tutor_id: int, tutor: Tutor):
    try:
        with engine.begin() as conn:
            sql = """UPDATE tutor 
                    SET nome = :nome, celular = :celular, endereco = :endereco 
                    WHERE id = :tutor_id"""

            dados = {
                "nome": tutor.nome,
                "celular": tutor.celular,
                "endereco": tutor.endereco,
                "tutor_id": tutor_id,
            }

            result = conn.execute(text(sql), dados)

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tutor não encontrado",
                )

            return {"message": "Tutor atualizado com sucesso!"}

    # Re-lança o HTTPException para não ser capturado pelo erro 500 genérico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar tutor: {str(e)}",
        )


@router.delete("/{tutor_id}")
def delete_tutor(tutor_id: int):
    try:
        with engine.begin() as conn:
            sql = """DELETE FROM tutor WHERE id = :tutor_id"""
            result = conn.execute(text(sql), {"tutor_id": tutor_id})

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tutor não encontrado",
                )

            return {"message": "Tutor deletado com sucesso!"}

    # Re-lança o HTTPException para não ser capturado pelo erro 500 genérico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar tutor: {str(e)}",
        )