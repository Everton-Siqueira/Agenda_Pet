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
        with engine.connect() as conn:
            sql = """INSERT INTO tutor (nome, celular, endereco) 
                    VALUES (:nome, :celular, :endereco)"""

            dados = {
                "nome": tutor.nome,
                "celular": tutor.celular,
                "endereco": tutor.endereco
            }

            conn.execute(text(sql), dados)
            conn.commit()
    except Exception as e:
        return {"error": str(e)}          
    
   
    return {"message": "Tutor criado com sucesso!"}

    