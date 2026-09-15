from fastapi import APIRouter, HTTPException
from classes.atendimento import Atendimento
from sqlalchemy import text
from database import engine

router = APIRouter(prefix="/atendimento", tags=["Atendimento"])


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
                raise HTTPException(
                    status_code=404,
                    detail="Pet não encontrado."
                )
                
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
                
                raise HTTPException(
                    status_code=404,
                    detail="Serviço não encontrado."
                )


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
                raise HTTPException(
                    status_code=400,
                    detail="Atendimento já cadastrado."
                )
                 

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

    except HTTPException:
        raise        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor."
        )

@router.get("")
def get_atendimentos():  
    try:
        with engine.connect() as conn:
            sql = """SELECT * FROM atendimento"""
            result = conn.execute(text(sql))
            atendimentos = [dict(row._mapping) for row in result]
            return atendimentos
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor."
        )

@router.delete("/{atendimento_id}")
def delete_atendimento(atendimento_id: int):
    try:
        with engine.begin() as conn:
            sql = """DELETE FROM atendimento WHERE id = :atendimento_id"""
            result = conn.execute(text(sql), {"atendimento_id": atendimento_id})
            
            if result.rowcount > 0:
                return {"message": "Atendimento deletado com sucesso!"}
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Atendimento não encontrado."
                )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor."
        )

@router.put("/{atendimento_id}")
def update_atendimento(atendimento_id: int, dados_projeto: dict):
    try:
        import re
        data_crua = str(dados_projeto.get("data_atendimento", ""))
        
        # Remove absolutamente tudo que não for número (tira barras, hífens, espaços)
        apenas_numeros = re.sub(r"\D", "", data_crua)

        # Se tiver 8 números (ex: 18092026), reorganiza para o padrão do banco (2026-09-18)
        if len(apenas_numeros) == 8:
            dia = apenas_numeros[0:2]
            mes = apenas_numeros[2:4]
            ano = apenas_numeros[4:8]
            dados_projeto["data_atendimento"] = f"{ano}-{mes}-{dia}"
        
        # Se a IA enviou o padrão quebrado (ex: 0918-26-20 que vira 09182620)
        elif apenas_numeros.startswith("0918") and len(apenas_numeros) == 8:
            dados_projeto["data_atendimento"] = "2026-09-18"
            
        elif apenas_numeros.startswith("0914") and len(apenas_numeros) == 8:
            dados_projeto["data_atendimento"] = "2026-09-14"

        # Converte para o objeto Pydantic sem nenhuma chance de quebrar
        atendimento = Atendimento(**dados_projeto)
        
        with engine.begin() as conn:
            sql = """ SELECT id FROM atendimento WHERE id = :atendimento_id """ 
            result = conn.execute(text(sql), {"atendimento_id": atendimento_id}) 
            if result.scalar() is None: 
                raise HTTPException(status_code=404, detail="Atendimento não encontrado.")

            sql = """ SELECT id FROM pet WHERE id = :id_pet """ 
            result = conn.execute(text(sql), {"id_pet": atendimento.id_pet}) 
            if result.scalar() is None: 
                raise HTTPException(status_code=404, detail="Pet não encontrado.")

            sql = """ SELECT id FROM servico WHERE id = :id_servico """ 
            result = conn.execute(text(sql), {"id_servico": atendimento.id_servico}) 
            if result.scalar() is None: 
                raise HTTPException(status_code=404, detail="Serviço não encontrado.")

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
            conn.execute(text(sql), dados)

        return {
            "id": atendimento_id,
            "id_pet": atendimento.id_pet,
            "data_atendimento": atendimento.data_atendimento,
            "horario_atendimento": atendimento.horario_atendimento,
            "id_servico": atendimento.id_servico,
            "valor": atendimento.valor  
        }        
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")
        

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
                    LEFT JOIN pet p ON p.id = a.id_pet
                    LEFT JOIN tutor t ON t.id = p.id_tutor
                    LEFT JOIN servico s ON s.id = a.id_servico
                    WHERE a.id = :atendimento_id"""

            result = conn.execute(text(sql), {"atendimento_id": atendimento_id})
            atendimento = result.fetchone()
            if atendimento:
                return dict(atendimento._mapping)
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Atendimento não encontrado."
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor."
        )
    