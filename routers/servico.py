import os
from fastapi import APIRouter
from dotenv import load_dotenv
from classes.servico import Servico
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

router = APIRouter(prefix="/servico", tags=["Serviço"])

engine = create_engine(DATABASE_URL)


@router.post("")
def create_servico(servico: Servico):
    try:
        with engine.connect() as conn:
            sql = """INSERT INTO servico (tipo_servico, valor) 
                    VALUES (:tipo_servico, :valor)"""

            dados = {
                "tipo_servico": servico.tipo_servico,
                "valor": servico.valor
            }

            conn.execute(text(sql), dados)
            conn.commit()
    except Exception as e:
        return {"error": str(e)}          
    
   
    return {"message": "Serviço criado com sucesso!"}

    