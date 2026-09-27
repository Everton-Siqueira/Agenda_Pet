from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from database import engine
from security import obter_usuario_logado

router = APIRouter(prefix="/atendimento", tags=["Atendimento / Agenda"])

@router.post("")
def create_atendimento(atendimento: dict, usuario: dict = Depends(obter_usuario_logado)):
    try:
        with engine.begin() as conn:
            sql = """INSERT INTO atendimento (id_pet, id_servico, data_hora, status, empresa_id) 
                    VALUES (:id_pet, :id_servico, :data_hora, :status, :empresa_id) RETURNING id"""
            dados = {
                "id_pet": atendimento.get("id_pet"),
                "id_servico": atendimento.get("id_servico"),
                "data_hora": atendimento.get("data_hora"),
                "status": atendimento.get("status", "Agendado"),
                "empresa_id": usuario["empresa_id"]
            }
            result = conn.execute(text(sql), dados)
            return {"message": "Agendamento criado com sucesso!", "id": result.fetchone()}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_atendimentos(usuario: dict = Depends(obter_usuario_logado)):
    try:
        with engine.connect() as conn:
            # Além de filtrar por empresa, fazemos um JOIN para trazer os nomes do pet e tutor na agenda de forma mastigada
            sql = """
                SELECT a.*, p.nome_pet, t.nome_tutor 
                FROM atendimento a
                JOIN pet p ON a.id_pet = p.id
                JOIN tutor t ON p.id_tutor = t.id
                WHERE a.empresa_id = :empresa_id
                ORDER BY a.data_hora ASC;
            """
            result = conn.execute(text(sql), {"empresa_id": usuario["empresa_id"]})
            return [dict(row._mapping) for row in result]
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.put("/{atendimento_id}")
def update_status_atendimento(atendimento_id: int, dados: dict, usuario: dict = Depends(obter_usuario_logado)):
    try:
        with engine.begin() as conn:
            sql = """UPDATE atendimento SET status = :status 
                    WHERE id = :atendimento_id AND empresa_id = :empresa_id"""
            result = conn.execute(text(sql), {
                "status": dados.get("status"),
                "atendimento_id": atendimento_id,
                "empresa_id": usuario["empresa_id"]
            })
            if result.rowcount == 0: raise HTTPException(status_code=404, detail="Agendamento não encontrado")
            return {"message": "Status do agendamento atualizado!"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))