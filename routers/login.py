from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from security import verificar_senha, criar_token_acesso, gerar_senha_hash # Import correto
from database import get_db
from pydantic import BaseModel, EmailStr
import traceback

# Modelo para receber as requisições de Login
class LoginDados(BaseModel):
    email: str
    senha: str

# Modelo para receber as requisições de Cadastro de Nova Empresa
class CadastroEmpresaDados(BaseModel):
    nome_empresa: str
    cnpj: str | None = None
    nome_admin: str
    email_admin: EmailStr
    senha_admin: str

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados_login: LoginDados, db = Depends(get_db)):
    try:
        # 1. Busca o funcionário pelo e-mail
        query = text("""
            SELECT id, empresa_id, senha_hash, nome, cargo 
            FROM public.funcionario 
            WHERE email = :email AND ativo = TRUE;
        """)
        result = db.execute(query, {"email": dados_login.email.strip()})
        funcionario = result.fetchone()

        # Validação se o usuário existe
        if not funcionario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail não encontrado no banco de dados."
            )

        # 2. Extração segura usando o padrão de mapeamento do SQLAlchemy
        dados_banco = funcionario._mapping
        id_usuario = dados_banco["id"]
        empresa_id = dados_banco["empresa_id"]
        senha_hash = dados_banco["senha_hash"]
        nome_usuario = dados_banco["nome"]
        cargo_usuario = dados_banco["cargo"]

        # 3. Validação da Senha
        if not verificar_senha(dados_login.senha, senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha incorreta para este usuário."
            )
            
        # 4. Montagem do Token convertendo UUIDs em strings puras
        dados_do_token = {
            "sub": str(id_usuario),
            "empresa_id": str(empresa_id),
            "cargo": str(cargo_usuario)
        }
        
        token = criar_token_acesso(dados_do_token)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "nome": str(nome_usuario),
                "cargo": str(cargo_usuario)
            }
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        erro_detalhado = f"Erro Interno no Python: {str(e)} -> Linha do erro: {traceback.format_exc()}"
        print(erro_detalhado)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no servidor ao autenticar."
        )

# ROTA: Cadastro de nova empresa com aproveitamento de dados existentes
@router.post("/registrar-empresa")
def registrar_empresa(dados: CadastroEmpresaDados, db = Depends(get_db)):
    try:
        # 1. Verifica se a empresa já existe (procurando por nome ou CNPJ se houver)
        if dados.cnpj:
            query_busca = text("SELECT id FROM public.empresa WHERE cnpj = :cnpj OR nome = :nome LIMIT 1;")
            result_busca = db.execute(query_busca, {"cnpj": dados.cnpj.strip(), "nome": dados.nome_empresa.strip()})
        else:
            query_busca = text("SELECT id FROM public.empresa WHERE nome = :nome LIMIT 1;")
            result_busca = db.execute(query_busca, {"nome": dados.nome_empresa.strip()})
            
        empresa_existente = result_busca.fetchone()

        if empresa_existente:
            empresa_id = empresa_existente._mapping["id"]
        else:
            # Se não existir, insere a nova empresa na tabela
            query_inserir_empresa = text("""
                INSERT INTO public.empresa (nome, cnpj) 
                VALUES (:nome, :cnpj) 
                RETURNING id;
            """)
            result_nova_empresa = db.execute(
                query_inserir_empresa, 
                {"nome": dados.nome_empresa.strip(), "cnpj": dados.cnpj.strip() if dados.cnpj else None}
            )
            empresa_id = result_nova_empresa.fetchone()[0]

        # 2. Verifica se o e-mail do administrador já está cadastrado
        query_busca_user = text("SELECT id FROM public.funcionario WHERE email = :email LIMIT 1;")
        user_existente = db.execute(query_busca_user, {"email": dados.email_admin.strip()}).fetchone()
        
        if user_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este e-mail de administrador já está cadastrado no sistema."
            )

        # 3. Cria o hash seguro usando a função importada corretamente
        senha_criptografada = gerar_senha_hash(dados.senha_admin)

        # 4. Insere o novo usuário vinculando ao empresa_id estabelecido
        query_inserir_usuario = text("""
            INSERT INTO public.funcionario (empresa_id, nome, email, senha_hash, cargo, ativo) 
            VALUES (:empresa_id, :nome, :email, :senha_hash, 'Administrador', TRUE);
        """)
        
        db.execute(query_inserir_usuario, {
            "empresa_id": empresa_id,
            "nome": dados.nome_admin.strip(),
            "email": dados.email_admin.strip(),
            "senha_hash": senha_criptografada
        })
        
        db.commit() # Confirma as alterações no banco de dados de vez

        return {
            "status": "sucesso",
            "message": "Empresa e Administrador cadastrados com sucesso!",
            "empresa_id": str(empresa_id)
        }

    except HTTPException as http_err:
        db.rollback()
        raise http_err
    except Exception as e:
        db.rollback()
        erro_detalhado = f"Erro ao registrar empresa: {str(e)} -> {traceback.format_exc()}"
        print(erro_detalhado)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor ao processar o cadastro."
        )