import re
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from database import engine
from datetime import date

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/resumo-gerencial")
def get_resumo_gerencial():
    try:
        hoje_str = date.today().isoformat()  # Retorna "2026-09-15"
        ano_atual = date.today().year       
        mes_atual = date.today().month      

        with engine.connect() as conn:
            # 1. TOTAL DE PETS CADASTRADOS NA BASE
            total_pets = conn.execute(text("SELECT COUNT(id) FROM pet")).scalar() or 0

            # 2. CONTROLE DE ATENDIMENTOS POR PERÍODO (Hoje, Semana, Mês, Ano)
            atend_hoje = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE data_atendimento = :hoje"
            ), {"hoje": hoje_str}).scalar() or 0
            
            atend_semana = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE data_atendimento >= DATE(:hoje, '-7 days')"
            ), {"hoje": hoje_str}).scalar() or 0
            
            atend_mes = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE strftime('%Y-%m', data_atendimento) = :mes"
            ), {"mes": f"{ano_atual}-{mes_atual:02d}"}).scalar() or 0
            
            atend_ano = conn.execute(text(
                "SELECT COUNT(id) FROM atendimento WHERE strftime('%Y', data_atendimento) = :ano"
            ), {"ano": str(ano_atual)}).scalar() or 0

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
                "SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE data_atendimento >= DATE(:hoje, '-7 days')"
            ), {"hoje": hoje_str}).scalar() or 0
            
            fat_mes = conn.execute(text(
                "SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE strftime('%Y-%m', data_atendimento) = :mes"
            ), {"mes": f"{ano_atual}-{mes_atual:02d}"}).scalar() or 0
            
            fat_ano = conn.execute(text(
                "SELECT COALESCE(SUM(valor), 0) FROM atendimento WHERE strftime('%Y', data_atendimento) = :ano"
            ), {"ano": str(ano_atual)}).scalar() or 0

            # 5. RANKING DE ASSIDUIDADE DOS ANIMAIS (Os mais atendidos no pet shop)
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

        # Retorna o JSON perfeitamente estruturado para mapear com o dashboard.tsx
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
            detail=f"Erro interno ao processar dados gerenciais do painel: {str(e)}")