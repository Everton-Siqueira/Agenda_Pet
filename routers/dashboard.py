from database import engine
from fastapi import APIRouter, HTTPException, status
from classes.dashboard import Dashboard
from sqlalchemy import text

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/top-tutores")
def get_top_tutores():
    try:
        with engine.connect() as conn:
            sql = """
                SELECT 
                    t.nome AS nome_tutor,
                    COUNT(a.id) AS total_agendamentos,
                    COALESCE(SUM(a.valor), 0) AS total_gasto
                FROM atendimento a
                LEFT JOIN pet p ON p.id = a.id_pet
                LEFT JOIN tutor t ON t.id = p.id_tutor
                GROUP BY t.id, t.nome
                ORDER BY total_agendamentos DESC
                LIMIT 5
            """
            result = conn.execute(text(sql))
            return [dict(row._mapping) for row in result]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter top tutores: {str(e)}"
        )
from database import engine
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/faturamento-consolidado")
def get_faturamento_consolidado():
    try:
        with engine.connect() as conn:
            # 1. Faturamento Total e Ticket Médio Geral
            sql_geral = """
                SELECT 
                    COALESCE(SUM(valor), 0) AS faturamento_total,
                    COALESCE(AVG(valor), 0) AS ticket_medio,
                    COUNT(*) AS total_atendimentos
                FROM atendimento
            """
            res_geral = conn.execute(text(sql_geral)).fetchone()

            # 2. Faturamento por Dia da Semana
            sql_dia_semana = """
                SELECT 
                    CASE EXTRACT(DOW FROM data_atendimento)
                        WHEN 0 THEN 'Domingo'
                        WHEN 1 THEN 'Segunda-feira'
                        WHEN 2 THEN 'Terça-feira'
                        WHEN 3 THEN 'Quarta-feira'
                        WHEN 4 THEN 'Quinta-feira'
                        WHEN 5 THEN 'Sexta-feira'
                        WHEN 6 THEN 'Sábado'
                    END AS dia_semana,
                    COUNT(*) AS total_atendimentos,
                    COALESCE(SUM(valor), 0) AS faturamento
                FROM atendimento
                GROUP BY EXTRACT(DOW FROM data_atendimento)
                ORDER BY EXTRACT(DOW FROM data_atendimento)
            """
            res_dia_semana = conn.execute(text(sql_dia_semana))

            # 3. Faturamento por Mês
            sql_mes = """
                SELECT 
                    TO_CHAR(data_atendimento, 'YYYY-MM') AS mes,
                    COUNT(*) AS total_atendimentos,
                    COALESCE(SUM(valor), 0) AS faturamento
                FROM atendimento
                GROUP BY TO_CHAR(data_atendimento, 'YYYY-MM')
                ORDER BY mes DESC
            """
            res_mes = conn.execute(text(sql_mes))

            # Monta o JSON unificado de resposta
            return {
                "resumo_geral": dict(res_geral._mapping),
                "faturamento_por_dia_semana": [
                    dict(row._mapping) for row in res_dia_semana
                ],
                "faturamento_por_mes": [dict(row._mapping) for row in res_mes],
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter relatório consolidado de faturamento: {str(e)}",
        
        )

@router.get("")
def get_dashboard():
    try:
        with engine.connect() as conn:
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

@router.get("/atendimentos-por-dia-semana")
def get_atendimentos_por_dia_semana():
    try:
        with engine.connect() as conn:
            sql = """
                SELECT 
                    CASE EXTRACT(DOW FROM data_atendimento)
                        WHEN 0 THEN 'Domingo'
                        WHEN 1 THEN 'Segunda-feira'
                        WHEN 2 THEN 'Terça-feira'
                        WHEN 3 THEN 'Quarta-feira'
                        WHEN 4 THEN 'Quinta-feira'
                        WHEN 5 THEN 'Sexta-feira'
                        WHEN 6 THEN 'Sábado'
                    END AS dia_semana,
                    COUNT(*) AS total_atendimentos
                FROM atendimento
                GROUP BY EXTRACT(DOW FROM data_atendimento)
                ORDER BY EXTRACT(DOW FROM data_atendimento)
            """

            result = conn.execute(text(sql))
            relatorio = [dict(row._mapping) for row in result]
            return relatorio

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dados do dashboard: {str(e)}",
        )
