import uvicorn
from fastapi import FastAPI

from routers import pet
from routers import tutor
from routers import servico
from routers import atendimento

app=FastAPI(
    title="API Petshop",
    description="API para gerenciamento de petshop",
    version="1.0.0"
)

app.include_router(pet.router)
app.include_router(tutor.router)
app.include_router(servico.router)
app.include_router(atendimento.router)



@app.get('/')
def index():
    return {"Hello" : "World"}

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=80,
        reload=True)