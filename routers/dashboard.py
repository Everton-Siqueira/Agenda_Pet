from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from database import engine
from datetime import date, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def formatar_servicos(resultados, coluna_qtd):
    """Filtra itens maiores que zero e formata a string"""
    itens = [f"{row[coluna_qtd]}x {row['tipo_servico']}" for row in resultados if row[coluna_qtd] > 0]
    return ", ".join(itens) if itens else "Nenhum serviço"

@router.get("/resumo-gerencial")
def get_resumo_gerencial():
    try:
        hoje = date.today()
        uma_semana_atras = hoje - timedelta(days=7)
        primeiro_dia_mes = date(hoje.year, hoje.month, 1)
        primeiro_dia_ano = date(hoje.year, 1, 1)

        parametros_data = {
            "hoje": hoje,
            "semana": uma_semana_atras,
            "inicio_mes": primeiro_dia_mes,
            "inicio_ano": primeiro_dia_ano
        }

        with engine.connect() as conn:
            # 1. TOTAL DE PETS (Mantém igual, pois olha para a tabela pet)
            total_pets = conn.execute(text("SELECT COUNT(id) FROM pet")).scalar() or 0

            # 2. ATENDIMENTOS E FATURAMENTO (Alinhado com a nova string 'concluido')
            # Regra: Faturamento soma apenas 'concluido'. Atendimentos conta tudo que não for 'cancelado'
            sql_metricas = """
                    SELECT 
                    COUNT(id) FILTER (WHERE data_atendimento = :hoje AND status != 'cancelado') as atend_hoje,
                    COUNT(id) FILTER (WHERE data_atendimento >= :semana AND status != 'cancelado') as atend_semana,
                    COUNT(id) FILTER (WHERE data_atendimento >= :inicio_mes AND status != 'cancelado') as atend_mes,
                    COALESCE(SUM(valor) FILTER (WHERE data_atendimento = :hoje AND status = 'concluido'), 0) as fat_hoje,
                    COALESCE(SUM(valor) FILTER (WHERE data_atendimento >= :semana AND status = 'concluido'), 0) as fat_semana,
                    COALESCE(SUM(valor) FILTER (WHERE data_atendimento >= :inicio_mes AND status = 'concluido'), 0) as fat_mes
                FROM atendimento
                WHERE data_atendimento >= :inicio_ano
            """
            metricas = conn.execute(text(sql_metricas), parametros_data).mappings().fetchone()

            # 2.B NOVO: FATURAMENTO MENSAL DETALHADO (De Janeiro a Dezembro)
            sql_meses = """
                SELECT 
                    EXTRACT(MONTH FROM TO_DATE(data_atendimento, 'DD/MM/YYYY')) as num_mes,
                    COALESCE(SUM(valor), 0) as total_mes
                FROM atendimento
                WHERE TO_DATE(data_atendimento, 'DD/MM/YYYY') >= :inicio_ano
                  AND status = 'concluido'
                GROUP BY EXTRACT(MONTH FROM TO_DATE(data_atendimento, 'DD/MM/YYYY'))
            """
            result_meses = conn.execute(text(sql_meses), parametros_data).mappings().fetchall()
            
            # Mapeia o resultado do banco para garantir que todos os 12 meses existam no retorno
            nomes_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            faturamento_por_mes = {int(row["num_mes"]): float(row["total_mes"]) for row in result_meses}
            
            consolidado_ano_detalhado = [
                {"mes": nomes_meses[m - 1], "valor": faturamento_por_mes.get(m, 0.0)}
                for m in range(1, 13)
            ]
            metricas = conn.execute(text(sql_metricas), parametros_data).mappings().fetchone()

            # 3. DETALHAMENTO DE SERVIÇOS (Apenas os concluidos)
            sql_servicos = """
                SELECT 
                    s.tipo_servico,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento = :hoje AND a.status = 'concluido') as qtd_hoje,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento >= :semana AND a.status = 'concluido') as qtd_semana,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento >= :inicio_mes AND a.status = 'concluido') as qtd_mes,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento >= :inicio_ano AND a.status = 'concluido') as qtd_ano
                FROM atendimento a
                JOIN servico s ON a.id_servico = s.id
                WHERE a.data_atendimento >= :inicio_ano 
                  AND a.status = 'concluido'
                GROUP BY s.tipo_servico
            """
            result_servicos = conn.execute(text(sql_servicos), parametros_data).mappings().fetchall()
            
            detalhe_hoje = formatar_servicos(result_servicos, "qtd_hoje")
            detalhe_semana = formatar_servicos(result_servicos, "qtd_semana")
            detalhe_mes = formatar_servicos(result_servicos, "qtd_mes")
            detalhe_ano = formatar_servicos(result_servicos, "qtd_ano")

            # 4. RANKING DE ASSIDUIDADE (Ignorar cancelados e pendentes - olha apenas concluidos)
            sql_ranking = """
                SELECT p.nome_pet, COUNT(a.id) as total_visitas
                FROM atendimento a
                JOIN pet p ON a.id_pet = p.id
                WHERE a.status = 'concluido'
                GROUP BY a.id_pet, p.nome_pet
                ORDER BY total_visitas DESC
                LIMIT 5
            """
            result_ranking = conn.execute(text(sql_ranking)).mappings().fetchall()
            ranking_list = [{"nome_pet": row["nome_pet"], "total_visitas": row["total_visitas"]} for row in result_ranking]

        return {
            "total_pets_cadastrados": total_pets,
            "servicos": {
                "hoje": detalhe_hoje,
                "semana": detalhe_semana,
                "mes": detalhe_mes,
                "ano": detalhe_ano
            },
            "atendimentos": {
                "hoje": metricas["atend_hoje"] or 0,
                "semana": metricas["atend_semana"] or 0,
                "mes": metricas["atend_mes"] or 0,
                "ano": metricas["atend_ano"] or 0
            },
            "faturamento": {
                "hoje": float(metricas["fat_hoje"]),
                "semana": float(metricas["fat_semana"]),
                "mes": float(metricas["fat_mes"]),
                "ano": float(metricas["fat_ano"])
            },
            "ranking_pets": ranking_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no painel: {str(e)}"
        )