from security import verificar_senha

senha = "Tati@102030"
hash_banco = "$2b$12$/aA8OSaaz6XADvx14gx7ou0aL/a0gi2QrgqMzULU1n9daFavRE7X6"

print("Resultado Passlib:", verificar_senha(senha, hash_banco))