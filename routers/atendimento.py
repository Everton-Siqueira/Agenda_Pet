import os
from fastapi import APIRouter
from dotenv import load_dotenv
from classes.atendimento import Atendimento
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

router = APIRouter(prefix="/atendimento", tags=["Atendimento"])

engine = create_engine(DATABASE_URL)

@router.post("")
def create_atendimento(atendimento: Atendimento):
    try:
        with engine.connect() as conn:
            sql = """INSERT INTO atendimento (id_pet, data_atendimento, id_servico, valor) 
                    VALUES (:id_pet, :data_atendimento, :id_servico, :valor)"""

            dados = {
                "id_pet": atendimento.id_pet,
                "data_atendimento": atendimento.data_atendimento,
                "id_servico": atendimento.id_servico,
                "valor": atendimento.valor
            }

            conn.execute(text(sql), dados)
            conn.commit()
    except Exception as e:
        return {"error": str(e)}          
    
   
    return {"message": "Atendimento criado com sucesso!"}

@router.get("")
def get_atendimentos():  
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM atendimento"""
            result = conn.execute(text(sql))
            atendimentos = [dict(row._mapping) for row in result]
            return atendimentos
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Atendimentos listados com sucesso!"}

@router.get("/{atendimento_id}")
def get_atendimento(atendimento_id: int):
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM atendimento WHERE id_atendimento = :atendimento_id"""
            result = conn.execute(text(sql), {"atendimento_id": atendimento_id})
            atendimento = result.fetchone()
            if atendimento:
                return dict(atendimento)
            else:
                return {"message": "Atendimento não encontrado"}
    except Exception as e:
        return {"error": str(e)}
    return {"message": "Atendimento listado com sucesso!"}

@router.delete("/{atendimento_id}")
def delete_atendimento(atendimento_id: int):
    try:
        with engine.connect() as conn:
            sql = """DELETE FROM atendimento WHERE id_atendimento = :atendimento_id"""
            result = conn.execute(text(sql), {"atendimento_id": atendimento_id})
            conn.commit()
            if result.rowcount > 0:
                return {"message": "Atendimento deletado com sucesso!"}
            else:
                return {"message": "Atendimento não encontrado"}
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Atendimento deletado com sucesso!"}

@router.put("/{atendimento_id}")
def update_atendimento(atendimento_id: int, atendimento: Atendimento):
    try:
        with engine.connect() as conn:
            sql = """UPDATE atendimento 
                    SET id_pet = :id_pet, data_atendimento = :data_atendimento, servico = :servico, valor = :valor 
                    WHERE id_atendimento = :atendimento_id"""

            dados = {
                "id_pet": atendimento.id_pet,
                "data_atendimento": atendimento.data_atendimento,
                "servico": atendimento.servico,
                "valor": atendimento.valor,
                "atendimento_id": atendimento_id
            }

            result = conn.execute(text(sql), dados)
            conn.commit()

            if result.rowcount == 0:
                return {"message": "Atendimento não encontrado"}
    except Exception as e:
        return {"error": str(e)}

    return {"message": "Atendimento atualizado com sucesso!"}      