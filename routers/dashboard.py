import re
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from database import engine
from datetime import date, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def obter_resumo_servicos(conn, condicao_sql, parametros):
    """Função auxiliar para agrupar e contar os nomes dos serviços no PostgreSQL"""
    sql = f"""
        SELECT s.tipo_servico, COUNT(a.id) as qtd
        FROM atendimento a
        JOIN servico s ON a.id_servico = s.id
        WHERE {condicao_sql}
        GROUP BY s.tipo_servico
        ORDER BY qtd DESC
    """
    result = conn.execute(text(sql), parametros)
    # Transforma o resultado em uma string limpa: "2x Banho, 1x Tosa"
    itens = [f"{row.qtd}x {row.tipo_servico}" for row in result]
    return ", ".join(itens) if itens else "Nenhum serviço"

@router.get("/resumo-gerencial")
def get_resumo_gerencial():
    try:
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        uma_semana_atras = hoje - timedelta(days=7)
        primeiro_dia_mes = date(hoje.year, hoje.month, 1)
        primeiro_dia_ano = date(hoje.year, 1, 1)

        with engine.connect() as conn:
            # TOTAL DE PETS CADASTRADOS NA BASE
            total_pets = conn.execute(text("SELECT COUNT(id) FROM pet")).scalar() or 0

            # 1. ATENDIMENTOS ISOLADOS POR PERÍODO
            atend_hoje = conn.execute(text("SELECT COUNT(id) FROM atendimento WHERE data_atendimento = :hoje"), {"hoje": hoje}).scalar() or 0
            atend_semana = conn.execute(text("SELECT COUNT(id) FROM atendimento WHERE data_atendimento >= :semana AND data_atendimento <= :ontem"), {"semana": uma_semana_atras, "ontem": ontem}).scalar() or 0
            atend_mes = conn.execute(text("SELECT COUNT(id) FROM atendimento WHERE data_atendimento >= :inicio_mes AND data_atendimento < :semana"), {"inicio_mes": primeiro_dia_mes, "semana": uma_semana_atras}).scalar() or 0
            atend_ano = conn.execute(text("SELECT COUNT(id) FROM atendimento WHERE data_atendimento >= :inicio_ano AND data_atendimento < :inicio_mes"), {"inicio_ano": primeiro_dia_ano, "inicio_mes": primeiro_dia_mes}).scalar() or 0

            # 2. DETALHAMENTO DE QUAIS SERVIÇOS FORAM FEITOS
            detalhe_hoje = obter_resumo_servicos(conn, "data_atendimento = :hoje", {"hoje": hoje})
            detalhe_semana = obter_resumo_servicos(conn, "data_atendimento >= :semana AND data_atendimento <= :ontem", {"semana": uma_semana_atras, "ontem": ontem})
            detalhe_mes = obter_resumo_servicos(conn, "data_atendimento >= :inicio_mes AND data_atendimento < :semana", {"inicio_mes": primeiro_dia_mes, "semana": uma_semana_atras})
            detalhe_ano = obter_resumo_servicos(conn, "data_atendimento >= :inicio_ano AND data_atendimento < :inicio_mes", {"inicio_ano": primeiro_dia_ano, "inicio_mes": primeiro_dia_mes})

            # 3. CONTROLE DE RECEBIMENTOS ISOLADOS (FATURAMENTO)
            fat_hoje = conn.execute(text("SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento = :hoje"), {"hoje": hoje}).scalar() or 0
            fat_semana = conn.execute(text("SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento >= :semana AND data_atendimento <= :ontem"), {"semana": uma_semana_atras, "ontem": ontem}).scalar() or 0
            fat_mes = conn.execute(text("SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento >= :inicio_mes AND data_atendimento < :semana"), {"inicio_mes": primeiro_dia_mes, "semana": uma_semana_atras}).scalar() or 0
            fat_ano = conn.execute(text("SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento >= :inicio_ano AND data_atendimento < :inicio_mes"), {"inicio_ano": primeiro_dia_ano, "inicio_mes": primeiro_dia_mes}).scalar() or 0

            # 4. RANKING DE ASSIDUIDADE DOS ANIMAIS
            sql_ranking = """
                SELECT p.nome_pet, COUNT(a.id) as total_visitas
                FROM atendimento a
                JOIN pet p ON a.id_pet = p.id
                GROUP BY a.id_pet, p.nome_pet
                ORDER BY total_visitas DESC
                LIMIT 5
            """
            result_ranking = conn.execute(text(sql_ranking))
            ranking_list = [{"nome_pet": row.nome_pet, "total_visitas": row.total_visitas} for row in result_ranking]

        return {
            "total_pets_cadastrados": total_pets,
            "servicos": {
                "hoje": detalhe_hoje,
                "semana": detalhe_semana,
                "mes": detalhe_mes,
                "ano": detalhe_ano
            },
            "atendimentos": {
                "hoje": atend_hoje,
                "semana": atend_semana,
                "mes": atend_mes,
                "ano": atend_ano
            },
            "faturamento": {
                "hoje": float(fat_hoje),
                "semana": float(fat_semana),
                "mes": float(fat_mes),
                "ano": float(fat_ano)
            },
            "ranking_pets": ranking_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no painel: {str(e)}"
        )