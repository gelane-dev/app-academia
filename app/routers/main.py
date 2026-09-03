from fastapi import FastAPI
from app.routers import auth, usuarios, admin, exercicios

app = FastAPI(
    title="Academia API",
    description="API gerenciamento de academia",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(admin.router)
app.include_router(exercicios.router)
