from fastapi import FastAPI
from app.routers import auth, usuarios, admin, exercicios, fichas, treino

app = FastAPI(
    title="Academia API",
    description="API gerenciamento de academia",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(admin.router)
app.include_router(exercicios.router)
app.include_router(fichas.router)
app.include_router(treino.router)