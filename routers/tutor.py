from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from database import engine
from security import obter_usuario_logado

router = APIRouter(prefix="/tutor", tags=["Tutor"])


@router.post("")
def create_tutor(
    tutor: dict,
    usuario: dict = Depends(obter_usuario_logado)
):
    try:
        with engine.begin() as conn:
            sql = """
                INSERT INTO tutor (
                    nome,
                    celular,
                    endereco,
                    empresa_id
                )
                VALUES (
                    :nome,
                    :celular,
                    :endereco,
                    :empresa_id
                )
                RETURNING id
            """

            dados = {
                "nome": tutor.get("nome"),
                "celular": tutor.get("celular"),
                "endereco": tutor.get("endereco"),
                "empresa_id": usuario["empresa_id"]
            }

            result = conn.execute(text(sql), dados)
            tutor_id = result.fetchone()[0]

            return {
                "message": "Tutor criado com sucesso!",
                "id": tutor_id
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar tutor: {str(e)}"
        )


@router.get("")
def get_tutores(
    usuario: dict = Depends(obter_usuario_logado)
):
    try:
        with engine.connect() as conn:
            sql = """
                SELECT *
                FROM tutor
                WHERE empresa_id = :empresa_id
            """

            result = conn.execute(
                text(sql),
                {"empresa_id": usuario["empresa_id"]}
            )

            return [dict(row._mapping) for row in result]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar tutores: {str(e)}"
        )


@router.get("/{tutor_id}")
def get_tutor(
    tutor_id: int,
    usuario: dict = Depends(obter_usuario_logado)
):
    try:
        with engine.connect() as conn:
            sql = """
                SELECT *
                FROM tutor
                WHERE id = :tutor_id
                AND empresa_id = :empresa_id
            """

            result = conn.execute(
                text(sql),
                {
                    "tutor_id": tutor_id,
                    "empresa_id": usuario["empresa_id"]
                }
            )

            tutor = result.fetchone()

            if tutor:
                return dict(tutor._mapping)

            raise HTTPException(
                status_code=404,
                detail="Tutor não encontrado"
            )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.put("/{tutor_id}")
def update_tutor(
    tutor_id: int,
    tutor: dict,
    usuario: dict = Depends(obter_usuario_logado)
):
    try:
        with engine.begin() as conn:
            sql = """
                UPDATE tutor
                SET
                    nome = :nome,
                    celular = :celular,
                    endereco = :endereco
                WHERE id = :tutor_id
                AND empresa_id = :empresa_id
            """

            dados = {
                "nome": tutor.get("nome"),
                "celular": tutor.get("celular"),
                "endereco": tutor.get("endereco"),
                "tutor_id": tutor_id,
                "empresa_id": usuario["empresa_id"]
            }

            result = conn.execute(text(sql), dados)

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Tutor não encontrado"
                )

            return {
                "message": "Tutor atualizado com sucesso!"
            }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete("/{tutor_id}")
def delete_tutor(
    tutor_id: int,
    usuario: dict = Depends(obter_usuario_logado)
):
    try:
        with engine.begin() as conn:
            sql = """
                DELETE FROM tutor
                WHERE id = :tutor_id
                AND empresa_id = :empresa_id
            """

            result = conn.execute(
                text(sql),
                {
                    "tutor_id": tutor_id,
                    "empresa_id": usuario["empresa_id"]
                }
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Tutor não encontrado"
                )

            return {
                "message": "Tutor deletado com sucesso!"
            }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )