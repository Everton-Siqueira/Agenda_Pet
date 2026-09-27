from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from classes.empresa import CadastroEmpresaSchema
from security import gerar_senha_hash
from database import get_db

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])

@router.post("", status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(dados: CadastroEmpresaSchema, db = Depends(get_db)):
    # Iniciamos uma transação segura. Se algo falhar, o SQLAlchemy desfaz tudo (Rollback) automaticamente
    with db.begin():
        try:
            # 1. Criação da Empresa no banco
            query_empresa = text("""
                INSERT INTO empresas (nome_comercial, razao_social, cnpj) 
                VALUES (:nome, :razao, :cnpj) RETURNING id;
            """)
            result_empresa = db.execute(query_empresa, {
                "nome": dados.nome_comercial,
                "razao": dados.razao_social,
                "cnpj": dados.cnpj
            })
            empresa_id = result_empresa.fetchone()[0]
            
            # 2. Criptografia da senha do primeiro funcionário (Dono)
            senha_criptografada = gerar_senha_hash(dados.senha_dono)
            
            # 3. Criação do primeiro funcionário atrelado a essa empresa
            query_funcionario = text("""
                INSERT INTO funcionarios (empresa_id, nome, email, senha_hash, cargo) 
                VALUES (:empresa_id, :nome, :email, :senha_hash, :cargo);
            """)
            db.execute(query_funcionario, {
                "empresa_id": empresa_id,
                "nome": dados.nome_dono,
                "email": dados.email_dono,
                "senha_hash": senha_criptografada,
                "cargo": "admin"
            })
            
            return {"mensagem": "Empresa e administrador criados com sucesso!", "empresa_id": str(empresa_id)}
            
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CNPJ informado ou o e-mail do administrador já estão cadastrados."
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))