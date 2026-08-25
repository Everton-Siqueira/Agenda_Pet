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
        with engine.begin() as conn:
            sql = """SELECT id
                FROM pet
                WHERE id = :id_pet"""

            result = conn.execute(text(sql), {"id_pet": atendimento.id_pet})
            id_pet_existente = result.scalar()


            if id_pet_existente is None:
                return {
                    "message": "Pet não encontrado."
                }

            sql = """
                SELECT id
                FROM servico
                WHERE id = :id_servico
                """

            result = conn.execute(
                text(sql),
                {"id_servico": atendimento.id_servico}
        )

            id_servico_existente = result.scalar()

            if id_servico_existente is None:
                return {
                    "message": "Serviço não encontrado."
                }


            sql = """SELECT id
                FROM atendimento
                WHERE id_pet = :id_pet AND data_atendimento = :data_atendimento AND horario_atendimento = :horario_atendimento"""

            result = conn.execute(text(sql), {
                "id_pet": atendimento.id_pet,
                "data_atendimento": atendimento.data_atendimento,
                "horario_atendimento": atendimento.horario_atendimento
            })

            id_existente = result.scalar()

            if id_existente is not None:
                return {"message": "Atendimento já cadastrado."
                } 

            sql = """INSERT INTO atendimento (id_pet, data_atendimento, horario_atendimento, id_servico, valor) 
                    VALUES (:id_pet, :data_atendimento, :horario_atendimento, :id_servico, :valor)
                    RETURNING id"""

            dados = {
                "id_pet": atendimento.id_pet,
                "data_atendimento": atendimento.data_atendimento,
                "horario_atendimento": atendimento.horario_atendimento,
                "id_servico": atendimento.id_servico,
                "valor": atendimento.valor
            }

            result = conn.execute(text(sql), dados)

            id_atendimento = result.scalar()

        return {
                "id": id_atendimento,
                "id_pet": atendimento.id_pet,
                "data_atendimento": atendimento.data_atendimento,
                "horario_atendimento": atendimento.horario_atendimento,
                "id_servico": atendimento.id_servico,
                "valor": atendimento.valor
    }
            
    except Exception as e:
        return {"error": str(e)}          
    
     
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

    
@router.delete("/{atendimento_id}")
def delete_atendimento(atendimento_id: int):
    try:
        with engine.begin() as conn:
            sql = """DELETE FROM atendimento WHERE id = :atendimento_id"""
            result = conn.execute(text(sql), {"atendimento_id": atendimento_id})
            
            if result.rowcount > 0:
                return {"message": "Atendimento deletado com sucesso!"}
            else:
                return {"message": "Atendimento não encontrado"}
    except Exception as e:
        return {"error": str(e)}

    

@router.put("/{atendimento_id}")
def update_atendimento(atendimento_id: int, atendimento: Atendimento):
    try:
        with engine.begin() as conn:
            sql = """ SELECT id 
            FROM atendimento 
            WHERE id = :atendimento_id """ 
            
            result = conn.execute( text(sql), 
                {"atendimento_id": atendimento_id} 
            ) 
            
            id_atendimento_existente = result.scalar() 
            
            if id_atendimento_existente is None: 
                return { "message": "Atendimento não encontrado." }

            sql = """ SELECT id 
                FROM pet 
                WHERE id = :id_pet """ 
            result = conn.execute( text(sql), 
            {"id_pet": atendimento.id_pet} 
            ) 
            
            id_pet_existente = result.scalar() 
            
            if id_pet_existente is None: 
                return { "message": "Pet não encontrado." }

            sql = """ SELECT id 
                FROM servico 
                WHERE id = :id_servico """ 
                
            result = conn.execute( text(sql), 
            {"id_servico": atendimento.id_servico} ) 
            id_servico_existente = result.scalar() 
            
            if id_servico_existente is None: 
                return { "message": "Serviço não encontrado." } 
                
            sql = """ SELECT id 
                FROM atendimento 
                WHERE id_pet = :id_pet AND data_atendimento = :data_atendimento AND horario_atendimento = :horario_atendimento AND id <> :atendimento_id """ 
                
            result = conn.execute( text(sql), 
                    { "id_pet": atendimento.id_pet, "data_atendimento": atendimento.data_atendimento, "horario_atendimento": atendimento.horario_atendimento, "atendimento_id": atendimento_id } ) 
                    
            id_existente = result.scalar() 
                    
            if id_existente is not None: 
                return { "message": "Já existe outro atendimento para este pet nessa data e horário." }    


            sql = """UPDATE atendimento 
                    SET id_pet = :id_pet, data_atendimento = :data_atendimento, horario_atendimento = :horario_atendimento, id_servico = :id_servico, valor = :valor 
                    WHERE id = :atendimento_id"""

            dados = {
                "id_pet": atendimento.id_pet,
                "data_atendimento": atendimento.data_atendimento,
                "horario_atendimento": atendimento.horario_atendimento,
                "id_servico": atendimento.id_servico,
                "valor": atendimento.valor,
                "atendimento_id": atendimento_id
            }

            result = conn.execute(text(sql), dados)

        return  {
            "id": atendimento_id,
            "id_pet": atendimento.id_pet,
            "data_atendimento": atendimento.data_atendimento,
            "horario_atendimento": atendimento.horario_atendimento,
            "id_servico": atendimento.id_servico,
            "valor": atendimento.valor  
            }        
            
    except Exception as e:
        return {"error": str(e)}
  
@router.get("/{atendimento_id}")
def get_atendimento(atendimento_id: int):
    try:
        with engine.connect() as conn:
            sql = """SELECT
                    a.id,
                    a.data_atendimento,
                    a.horario_atendimento,
                    t.nome AS nome_tutor,
                    p.nome_pet,
                    s.tipo_servico AS servico,
                    a.valor
                FROM atendimento a
                    JOIN pet p ON p.id = a.id_pet
                    JOIN tutor t ON t.id = p.id_tutor
                    JOIN servico s ON s.id = a.id_servico
                    WHERE a.id = :atendimento_id"""

            result = conn.execute(text(sql), {"atendimento_id": atendimento_id})
            atendimento = result.fetchone()
            if atendimento:
                return dict(atendimento._mapping)
            else:
                return {"message": "Atendimento não encontrado"}
    except Exception as e:
        return {"error": str(e)}
    