from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from database import engine
from datetime import date, timedelta
from security import obter_usuario_logado  # Injetada a trava de segurança

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def formatar_servicos(resultados, coluna_qtd):
    """Filtra itens maiores que zero e formata a string"""
    itens = [f"{row[coluna_qtd]}x {row['tipo_servico']}" for row in resultados if row[coluna_qtd] > 0]
    return ", ".join(itens) if itens else "Nenhum serviço"

@router.get("/resumo-gerencial")
def get_resumo_gerencial(usuario: dict = Depends(obter_usuario_logado)):
    try:
        # Extrai o ID da empresa do Token JWT de forma blindada
        empresa_id = usuario["empresa_id"]

        hoje = date.today()
        uma_semana_atras = hoje - timedelta(days=7)
        primeiro_dia_mes = date(hoje.year, hoje.month, 1)
        primeiro_dia_ano = date(hoje.year, 1, 1)

        # Adicionado o empresa_id nos parâmetros compartilhados das consultas SQL
        parametros_data = {
            "hoje": hoje,
            "semana": uma_semana_atras,
            "inicio_mes": primeiro_dia_mes,
            "inicio_ano": primeiro_dia_ano,
            "empresa_id": empresa_id
        }

        with engine.connect() as conn:
            # 1. TOTAL DE PETS (Isolado por empresa)
            total_pets = conn.execute(
                text("SELECT COUNT(id) FROM pet WHERE empresa_id = :empresa_id"),
                {"empresa_id": empresa_id}
                ).scalar() or 0

            # 2. ATENDIMENTOS E FATURAMENTO (Isolado com WHERE empresa_id)
            sql_metricas = """
                SELECT 
                COUNT(id) FILTER (WHERE data_atendimento = :hoje AND status != 'cancelado') as atend_hoje,
                COUNT(id) FILTER (WHERE data_atendimento >= :semana AND status != 'cancelado') as atend_semana,
                COUNT(id) FILTER (WHERE data_atendimento >= :inicio_mes AND status != 'cancelado') as atend_mes,
                COUNT(id) FILTER (WHERE data_atendimento >= :inicio_ano AND status != 'cancelado') as atend_ano,
                    
                COALESCE(SUM(valor) FILTER (WHERE data_atendimento = :hoje AND status = 'concluido'), 0) as fat_hoje,
                COALESCE(SUM(valor) FILTER (WHERE data_atendimento >= :semana AND status = 'concluido'), 0) as fat_semana,
                COALESCE(SUM(valor) FILTER (WHERE data_atendimento >= :inicio_mes AND status = 'concluido'), 0) as fat_mes,
                COALESCE(SUM(valor) FILTER (WHERE data_atendimento >= :inicio_ano AND status = 'concluido'), 0) as fat_ano
                FROM atendimento
                WHERE data_atendimento >= :inicio_ano AND empresa_id = :empresa_id
            """
            metricas = conn.execute(text(sql_metricas), parametros_data).mappings().fetchone()

            # 2.B FATURAMENTO MENSAL DETALHADO (Isolado com WHERE empresa_id)
            sql_meses = """
                SELECT 
                    CAST(EXTRACT(MONTH FROM data_atendimento) AS INTEGER) as num_mes,
                    COALESCE(SUM(valor), 0) as total_mes
                FROM atendimento
                WHERE data_atendimento >= :inicio_ano
                  AND status = 'concluido'
                  AND empresa_id = :empresa_id
                GROUP BY EXTRACT(MONTH FROM data_atendimento)
                ORDER BY num_mes ASC
            """
            result_meses = conn.execute(text(sql_meses), parametros_data).mappings().fetchall()
            
            nomes_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            faturamento_por_mes = {int(row["num_mes"]): float(row["total_mes"]) for row in result_meses}
            
            consolidado_ano_detalhado = [
                {"mes": nomes_meses[m - 1], "valor": faturamento_por_mes.get(m, 0.0)}
                for m in range(1, 13)
            ]

            # 3. DETALHAMENTO DE SERVIÇOS (Garantido relacionamento correto com empresa_id)
            sql_servicos = """
                SELECT 
                    s.tipo_servico,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento = :hoje AND a.status = 'concluido') as qtd_hoje,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento >= :semana AND a.status = 'concluido') as qtd_semana,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento >= :inicio_mes AND a.status = 'concluido') as qtd_mes,
                    COUNT(a.id) FILTER (WHERE a.data_atendimento >= :inicio_ano AND a.status = 'concluido') as qtd_ano
                FROM atendimento a
                JOIN servico s ON a.id_servico = s.id AND s.empresa_id = a.empresa_id
                WHERE a.data_atendimento >= :inicio_ano 
                  AND a.status = 'concluido'
                  AND a.empresa_id = :empresa_id
                GROUP BY s.tipo_servico
            """
            result_servicos = conn.execute(text(sql_servicos), parametros_data).mappings().fetchall()
            
            detalhe_hoje = formatar_servicos(result_servicos, "qtd_hoje")
            detalhe_semana = formatar_servicos(result_servicos, "qtd_semana")
            detalhe_mes = formatar_servicos(result_servicos, "qtd_mes")
            detalhe_ano = formatar_servicos(result_servicos, "qtd_ano")

            # 4. RANKING DE ASSIDUIDADE (Isolado por empresa_id)
            sql_ranking = """
                SELECT p.nome_pet, COUNT(a.id) as total_visitas
                FROM atendimento a
                JOIN pet p ON a.id_pet = p.id AND p.empresa_id = a.empresa_id
                WHERE a.status = 'concluido' AND a.empresa_id = :empresa_id
                GROUP BY a.id_pet, p.nome_pet
                ORDER BY total_visitas DESC
                LIMIT 5
            """
            result_ranking = conn.execute(text(sql_ranking), {"empresa_id": empresa_id}).mappings().fetchall()
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
            "ranking_pets": ranking_list,
            "consolidado_ano_detalhado": consolidado_ano_detalhado
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no painel: {str(e)}"
        )