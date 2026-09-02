from pydantic import BaseModel
from typing import Optional

class ExercicioCriar(BaseModel):
    nome: str
    descricao: str
    grupo_muscular: str

class ExercicioAtualizar(BaseModel):
    nome: str
    descricao: str
    grupo_muscular: str

class ExercicioResposta(BaseModel):
    id: int
    nome: str
    descricao: str
    grupo_muscular: str
    imagem: str | None = None
    video: str | None = None