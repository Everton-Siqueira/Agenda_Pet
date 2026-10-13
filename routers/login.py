from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from security import verificar_senha, criar_token_acesso, gerar_senha_hash
from database import get_db
from pydantic import BaseModel

class LoginDados(BaseModel):
    email: str
    senha: str

class CadastroEmpresaDados(BaseModel):
    nome_empresa: str
    cnpj: str | None = None
    nome_admin: str
    email_admin: str
    senha_admin: str

router = APIRouter(prefix="/api/login", tags=["Autenticação"])

@router.post("")
def login(dados: LoginDados, db = Depends(get_db)):
    query = text("SELECT id, empresa_id, senha_hash, nome, cargo FROM public.funcionario WHERE email = :email AND ativo = TRUE;")
    user = db.execute(query, {"email": dados.email.strip()}).fetchone()

    if not user or not verificar_senha(dados.senha, user._mapping["senha_hash"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
        
    token = criar_token_acesso({
        "sub": str(user._mapping["id"]),
        "empresa_id": str(user._mapping["empresa_id"]),
        "cargo": str(user._mapping["cargo"])
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {"nome": user._mapping["nome"], "cargo": user._mapping["cargo"]}
    }

@router.post("/registrar-empresa")
def registrar_empresa(dados: CadastroEmpresaDados, db = Depends(get_db)):
    # 1. Verifica duplicidade de e-mail antes de abrir a transação
    email_existe = db.execute(text("SELECT id FROM public.funcionario WHERE email = :email LIMIT 1;"), {"email": dados.email_admin.strip()}).fetchone()
    if email_existe:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")

    # O 'with db.begin()' gerencia o commit e garante que grave no PostgreSQL perfeitamente
    with db.begin():
        # 2. Busca ou Insere a Empresa
        empresa = db.execute(text("SELECT id FROM public.empresa WHERE cnpj = :cnpj OR nome_comercial = :nome LIMIT 1;"), {"cnpj": dados.cnpj, "nome": dados.nome_empresa}).fetchone()
        
        if empresa:
            empresa_id = empresa[0]
        else:
            query_empresa = text("INSERT INTO public.empresa (nome_comercial, razao_social, cnpj, criado_em, ativo) VALUES (:nome, :nome, :cnpj, NOW(), TRUE) RETURNING id;")
            empresa_id = db.execute(query_empresa, {"nome": dados.nome_empresa.strip(), "cnpj": dados.cnpj}).fetchone()[0]

        # 3. Insere o Administrador extraindo o ID numérico correto
        query_user = text("""
            INSERT INTO public.funcionario (empresa_id, nome, email, senha_hash, cargo, ativo) 
            VALUES (:empresa_id, :nome, :email, :senha, 'Administrador', TRUE);
        """)
        db.execute(query_user, {
            "empresa_id": int(empresa_id),
            "nome": dados.nome_admin.strip(),
            "email": dados.email_admin.strip(),
            "senha": gerar_senha_hash(dados.senha_admin)
        })

    return {"status": "sucesso", "message": "Cadastro realizado com sucesso!"}