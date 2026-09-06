from database import engine
from fastapi import APIRouter, HTTPException
from classes.dashboard import Dashboard
from sqlalchemy import text

@router.get("/dashboard")
def get_dashboard():
    try:
        with engine.begin() as conn:
            sql = """
                SELECT 
                    (SELECT COUNT(*) FROM pet) AS total_pets,
                    (SELECT COUNT(*) FROM servico) AS total_servicos,
                    (SELECT COUNT(*) FROM atendimento) AS total_atendimentos
            """

            result = conn.execute(text(sql))
            row = result.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Não foi possível obter os dados do dashboard."
                )

            dashboard_data = Dashboard(
                total_pets=row.total_pets,
                total_servicos=row.total_servicos,
                total_atendimentos=row.total_atendimentos
            )

            return dashboard_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter dados do dashboard: {str(e)}"
        )
        