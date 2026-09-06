from database import engine
from fastapi import APIRouter, HTTPException
from classes.servico import Servico
from sqlalchemy import text


router = APIRouter(prefix="/servico", tags=["Serviço"])

@router.post("")
def create_servico(servico: Servico):
    try:
        with engine.begin() as conn:
            sql = """
                SELECT id
                FROM servico
                WHERE tipo_servico = :tipo_servico
            """

            result = conn.execute(
                text(sql),
                {"tipo_servico": servico.tipo_servico}
            )

            id_existente = result.scalar()

            if id_existente is not None:
                raise HTTPException(
                    status_code=400,
                    detail="Serviço já cadastrado."
                )



            sql = """INSERT INTO servico (tipo_servico, valor) 
                    VALUES (:tipo_servico, :valor)
                    RETURNING id
                    """

            
            dados = {
                "tipo_servico": servico.tipo_servico,
                "valor": servico.valor
            }

            result = conn.execute(text(sql), dados)

            id_servico = result.scalar()

            return {"id": id_servico,
                    "tipo_servico": servico.tipo_servico,
                    "valor": servico.valor
            }

    except HTTPException:
        raise        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar serviço: {str(e)}"  
        )     
    
    
@router.get("")
def get_servicos():  
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM servico"""
            result = conn.execute(text(sql))
            servicos = [dict(row._mapping) for row in result]
            return servicos
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar serviços: {str(e)}"
        )

    
@router.get("/{servico_id}")
def get_servico(servico_id: int):   
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM servico WHERE id = :servico_id"""
            result = conn.execute(text(sql), {"servico_id": servico_id})
            servico = result.fetchone()
            if servico:
                return dict(servico._mapping)
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Serviço não encontrado"
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar serviço: {str(e)}"
        )

    
@router.put("/{servico_id}")
def update_servico(servico_id: int, servico: Servico):
    try:
        with engine.begin() as conn:
            sql = """UPDATE servico 
                    SET tipo_servico = :tipo_servico, valor = :valor 
                    WHERE id = :servico_id"""

            dados = {
                "tipo_servico": servico.tipo_servico,
                "valor": servico.valor,
                "servico_id": servico_id
            }

            result = conn.execute(text(sql), dados)
           

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Serviço não encontrado"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar serviço: {str(e)}"
        )

    return {"message": "Serviço atualizado com sucesso!"}

@router.delete("/{servico_id}")
def delete_servico(servico_id: int):
    try:
        with engine.begin() as conn:
            sql = """DELETE FROM servico WHERE id = :servico_id"""
            result = conn.execute(text(sql), {"servico_id": servico_id})
            

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Serviço não encontrado"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar serviço: {str(e)}"
        )

    return {"message": "Serviço deletado com sucesso!"} 

    