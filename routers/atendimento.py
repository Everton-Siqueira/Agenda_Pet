from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy import text
from database import engine
from security import obter_usuario_logado
from classes.atendimento import Atendimento


router = APIRouter(prefix="/atendimento", tags=["Atendimento / Agenda"])


@router.post("")
def create_atendimento(
    atendimento: Atendimento,  # 🟢 O Pydantic valida e limpa a data "25102026" automaticamente
    usuario: dict = Depends(obter_usuario_logado)  # 🔒 Identifica quem está logado
):
    try:
        with engine.begin() as conn:
            sql = """
                INSERT INTO atendimento (
                    id_pet,
                    id_servico,
                    data_atendimento,
                    horario_atendimento,
                    valor,
                    status,
                    empresa_id
                )
                VALUES (
                    :id_pet,
                    :id_servico,
                    :data_atendimento,
                    :horario_atendimento,
                    :valor,
                    :status,
                    :empresa_id
                )
                RETURNING id
            """

            dados = {
                "id_pet": atendimento.id_pet,
                "id_servico": atendimento.id_servico,
                "data_atendimento": atendimento.data_atendimento,  # Objeto date seguro convertido pela classe
                "horario_atendimento": atendimento.horario_atendimento,
                "valor": atendimento.valor,
                "status": atendimento.status,
                "empresa_id": usuario["empresa_id"]  # 🔒 Vincula obrigatoriamente à empresa do usuário logado
            }

            result = conn.execute(text(sql), dados)

            return {
                "message": "Agendamento criado com sucesso!",
                "id": result.fetchone()[0]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def get_atendimentos(
    usuario: dict = Depends(obter_usuario_logado)  # 🔒 Identifica quem está logado
):
    try:
        with engine.connect() as conn:
            # 🔒 JOINs e WHERE garantem isolamento total entre os clientes do banco
            sql = """
                SELECT
                    a.*,
                    p.nome_pet,
                    t.nome AS nome_tutor
                FROM atendimento a
                JOIN pet p
                    ON a.id_pet = p.id
                    AND p.empresa_id = a.empresa_id
                JOIN tutor t
                    ON p.id_tutor = t.id
                    AND t.empresa_id = a.empresa_id
                WHERE a.empresa_id = :empresa_id
                ORDER BY
                    a.data_atendimento ASC,
                    a.horario_atendimento ASC;
            """

            result = conn.execute(
                text(sql),
                {"empresa_id": usuario["empresa_id"]}  # 🔒 Filtra apenas dados da empresa atual
            )

            return [dict(row._mapping) for row in result]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{atendimento_id}")
def update_atendimento(
    atendimento_id: int,
    dados: Atendimento,  # 🟢 Usa a classe de validação na atualização também
    usuario: dict = Depends(obter_usuario_logado)  # 🔒 Identifica quem está logado
):
    try:
        with engine.begin() as conn:
            # 🔒 O WHERE garante que o usuário só consiga atualizar registros da própria empresa
            sql = """
                UPDATE atendimento
                SET 
                    id_pet = :id_pet,
                    id_servico = :id_servico,
                    data_atendimento = :data_atendimento,
                    horario_atendimento = :horario_atendimento,
                    valor = :valor,
                    status = :status
                WHERE id = :atendimento_id
                AND empresa_id = :empresa_id
            """

            result = conn.execute(
                text(sql),
                {
                    "id_pet": dados.id_pet,
                    "id_servico": dados.id_servico,
                    "data_atendimento": dados.data_atendimento,
                    "horario_atendimento": dados.horario_atendimento,
                    "valor": dados.valor,
                    "status": dados.status,
                    "atendimento_id": atendimento_id,
                    "empresa_id": usuario["empresa_id"]  # 🔒 Bloqueia alterações em registros de terceiros
                }
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Agendamento não encontrado ou sem permissão para alterar."
                )

            return {
                "message": "Agendamento atualizado com sucesso!"
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.patch("/{atendimento_id}/status")
def update_status_atendimento(
    atendimento_id: int,
    dados: dict = Body(...),
    usuario: dict = Depends(obter_usuario_logado)
):
    novo_status = dados.get("status")

    if novo_status not in ["pendente", "concluido", "cancelado"]:
        raise HTTPException(
            status_code=400,
            detail="Status inválido."
        )

    try:
        with engine.begin() as conn:
            sql = """
                UPDATE atendimento
                SET status = :status
                WHERE id = :atendimento_id
                AND empresa_id = :empresa_id
            """

            result = conn.execute(
                text(sql),
                {
                    "status": novo_status,
                    "atendimento_id": atendimento_id,
                    "empresa_id": usuario["empresa_id"]
                }
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Agendamento não encontrado ou sem permissão para alterar."
                )

            return {
                "message": "Status do atendimento atualizado com sucesso!",
                "status": novo_status
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.delete("/{atendimento_id}")
def delete_atendimento(
    atendimento_id: int,
    usuario: dict = Depends(obter_usuario_logado)
):
    try:
        with engine.begin() as conn:
            sql = """
                DELETE FROM atendimento
                WHERE id = :atendimento_id
                AND empresa_id = :empresa_id
            """

            result = conn.execute(
                text(sql),
                {
                    "atendimento_id": atendimento_id,
                    "empresa_id": usuario["empresa_id"]
                }
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Agendamento não encontrado ou sem permissão para excluir."
                )

            return {
                "message": "Agendamento excluído com sucesso!"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
