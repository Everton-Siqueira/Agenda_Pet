from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from database import engine
from security import obter_usuario_logado

router = APIRouter(prefix="/servico", tags=["Serviço"])

@router.post("")
def create_servico(servico: dict, usuario: dict = Depends(obter_usuario_logado)):
    try:
        with engine.begin() as conn:
            sql = """INSERT INTO servico (nome_servico, preco, empresa_id) 
                    VALUES (:nome_servico, :preco, :empresa_id) RETURNING id"""
            dados = {
                "nome_servico": servico.get("nome_servico"),
                "preco": servico.get("preco"),
                "empresa_id": usuario["empresa_id"]
            }
            result = conn.execute(text(sql), dados)
            return {"message": "Serviço criado com sucesso!", "id": result.fetchone()}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_servicos(usuario: dict = Depends(obter_usuario_logado)):
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM servico WHERE empresa_id = :empresa_id"""
            result = conn.execute(text(sql), {"empresa_id": usuario["empresa_id"]})
            return [dict(row._mapping) for row in result]
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.put("/{servico_id}")
def update_servico(servico_id: int, servico: dict, usuario: dict = Depends(obter_usuario_logado)):  
    try:
        with engine.begin() as conn:
            sql = """UPDATE servico SET nome_servico = :nome_servico, preco = :preco 
                    WHERE id = :servico_id AND empresa_id = :empresa_id"""
            dados = {
                "nome_servico": servico.get("nome_servico"),
                "preco": servico.get("preco"),
                "servico_id": servico_id,
                "empresa_id": usuario["empresa_id"]
            }
            result = conn.execute(text(sql), dados)
            if result.rowcount == 0: raise HTTPException(status_code=404, detail="Serviço não encontrado")
            return {"message": "Serviço atualizado com sucesso!"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{servico_id}")
def delete_servico(servico_id: int, usuario: dict = Depends(obter_usuario_logado)):    
    try:
        with engine.begin() as conn:
            sql = """DELETE FROM servico WHERE id = :servico_id AND empresa_id = :empresa_id"""
            result = conn.execute(text(sql), {"servico_id": servico_id, "empresa_id": usuario["empresa_id"]})
            if result.rowcount == 0: raise HTTPException(status_code=404, detail="Serviço não encontrado")
            return {"message": "Serviço deletado com sucesso!"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))