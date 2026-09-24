import re
import logging
import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from classes.login import LoginRequest, LoginResponse
from sqlalchemy import text
from database import engine

router = APIRouter(prefix="/login", tags=["Login"])

@router.post("")
def login(login_request: LoginRequest):
    try:
        with engine.begin() as conn:
            sql = """SELECT id, email, senha, id_empresa
                FROM empresa
                WHERE email = :email"""

            result = conn.execute(text(sql), {"email": login_request.email})
            tutor = result.fetchone()

            if tutor is None:
                raise HTTPException(
                    status_code=401,
                    detail="Credenciais inválidas."
                )

            if tutor.senha != login_request.senha:
                raise HTTPException(
                    status_code=401,
                    detail="Credenciais inválidas."
                )

            # Gerar token JWT
            payload = {
                "id": tutor.id,
                "nome": tutor.nome,
                "email": tutor.email
            }
            token = jwt.encode(payload, "sua_chave_secreta", algorithm="HS256")

            return LoginResponse(token=token)

    except Exception as e:
        logging.error(f"Erro ao realizar login: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor."
        )


