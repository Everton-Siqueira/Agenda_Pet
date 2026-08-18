import os
from fastapi import APIRouter
from dotenv import load_dotenv
from classes.tutor import Tutor
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
print(DATABASE_URL)

router = APIRouter(prefix="/tutor", tags=["Tutor"])

engine = create_engine(DATABASE_URL)


@router.post("")
def create_tutor(tutor: Tutor):
    try:
        with engine.begin() as conn:
            sql = """INSERT INTO tutor (nome, celular, endereco) 
                    VALUES (:nome, :celular, :endereco)"""

            dados = {
                "nome": tutor.nome,
                "celular": tutor.celular,
                "endereco": tutor.endereco
            }

            conn.execute(text(sql), dados)
            
    except Exception as e:
        return {"error": str(e)}          
    
   
    return {"message": "Tutor criado com sucesso!"}

@router.get("")
def get_tutores():
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM tutor"""
            result = conn.execute(text(sql))
            tutores = [dict(row._mapping) for row in result]
            return tutores
    except Exception as e:
        return {"error": str(e)}

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
                return {"message": "Tutor não encontrado"}
    except Exception as e:
        return {"error": str(e)}

@router.put("/{tutor_id}")
def update_tutor(tutor_id: int, tutor: Tutor):
    try:
        with engine.begin() as conn:
            sql = """UPDATE tutor SET nome = :nome, celular = :celular, endereco = :endereco 
                    WHERE id = :tutor_id"""

            dados = {
                "nome": tutor.nome,
                "celular": tutor.celular,
                "endereco": tutor.endereco,
                "tutor_id": tutor_id
            }

            result = conn.execute(text(sql), dados)
            

            if result.rowcount == 0:
                return {"message": "Tutor não encontrado"}
    except Exception as e:
        return {"error": str(e)}          
    
   
    return {"message": "Tutor atualizado com sucesso!"}

@router.delete("/{tutor_id}")
def delete_tutor(tutor_id: int):
    try:
        with engine.begin() as conn:
            sql = """DELETE FROM tutor WHERE id = :tutor_id"""
            result = conn.execute(text(sql), {"tutor_id": tutor_id})
            

            if result.rowcount == 0:
                return {"message": "Tutor não encontrado"}
    except Exception as e:
        return {"error": str(e)}          
    
   
    return {"message": "Tutor deletado com sucesso!"}           

    