import uvicorn
from fastapi import FastAPI

from routers import pet
from routers import tutor
from routers import servico
from routers import atendimento
from routers import dashboard

app=FastAPI(
    title="API Petshop",
    description="API para gerenciamento de petshop",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

# ATENÇÃO: Adicione este bloco logo após criar a variável 'app'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que qualquer frontend (web ou celular) acesse sua API
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

app.include_router(pet.router)
app.include_router(tutor.router)
app.include_router(servico.router)
app.include_router(atendimento.router)
app.include_router(dashboard.router)



@app.get('/')
def index():
    return {"Hello" : "World"}

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True)