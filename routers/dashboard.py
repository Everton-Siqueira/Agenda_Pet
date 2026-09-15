import re
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from database import engine
from datetime import date, timedelta  # ADICIONADO: timedelta para cálculo nativo no Python

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/resumo-gerencial")
def get_resumo_gerencial():
    try:
        # 1. CÁLCULO DE DATAS NATIVO NO PYTHON (Evita erros de sintaxe SQL/SQLite)
        hoje = date.today()
        hoje_str = hoje.isoformat()                     # Ex: "2026-09-15"
        
        uma_semana_atras = hoje - timedelta(days=7)     # Calcula 7 dias atrás de forma nativa
        semana_str = uma_semana_atras.isoformat()        # Ex: "2026-09-08"
        
        mes_prefixo = f"{hoje.year}-{hoje.month:02d}%"  # Ex: "2026-09%" (para busca via LIKE)
        ano_prefixo = f"{hoje.year}%"                    # Ex: "2026%" (para busca via LIKE)

        with engine.connect() as conn:
            # TOTAL DE PETS CADASTRADOS
            total_pets = conn.execute(text("SELECT COUNT(id) FROM pet")).scalar() or 0

            # 2. CONTROLE DE ATENDIMENTOS POR PERÍODO (Hoje, Semana, Mês, Ano)
            atend_hoje = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE data_atendimento = :hoje"
            ), {"hoje": hoje_str}).scalar() or 0
            
            atend_semana = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE data_atendimento >= :semana"
            ), {"semana": semana_str}).scalar() or 0
            
            atend_mes = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE data_atendimento LIKE :mes"
            ), {"mes": mes_prefixo}).scalar() or 0
            
            atend_ano = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE data_atendimento LIKE :ano"
            ), {"ano": ano_prefixo}).scalar() or 0

            # 3. CONTROLE DE SERVIÇOS REALIZADOS POR PERÍODO
            serv_hoje = atend_hoje
            serv_semana = atend_semana
            serv_mes = atend_mes
            serv_ano = atend_ano

            # 4. CONTROLE DE RECEBIMENTOS (FATURAMENTO) POR PERÍODO
            fat_hoje = conn.execute(text(
                "SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento = :hoje"
            ), {"hoje": hoje_str}).scalar() or 0
            
            fat_semana = conn.execute(text(
                "SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento >= :semana"
            ), {"semana": semana_str}).scalar() or 0
            
            fat_mes = conn.execute(text(
                "SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento LIKE :mes"
            ), {"mes": mes_prefixo}).scalar() or 0
            
            fat_ano = conn.execute(text(
                "SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento LIKE :ano"
            ), {"ano": ano_prefixo}).scalar() or 0

            # 5. RANKING DE ASSIDUIDADE DOS ANIMAIS (Os 5 mais atendidos)
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

        # Retorna a estrutura perfeita para o dashboard.tsx
        return {
            "total_pets_cadastrados": total_pets,
            "servicos": {
                "hoje": serv_hoje,
                "semana": serv_semana,
                "mes": serv_mes,
                "ano": serv_ano
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
            detail=f"Erro interno ao processar dados gerenciais do painel: {str(e)}"
        )