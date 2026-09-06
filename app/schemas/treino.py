from pydantic import BaseModel, EmailStr

class TreinoCriar(BaseModel):
    ficha_id: int
    nome: str
    dia_semana: str
    ordem: int

class TreinoResposta(BaseModel):
    id: int
    ficha_id: int
    nome: str
    dia_semana: str
    ordem: int

class AtualizarTreino(BaseModel):
    nome: str
    dia_semana: str
    ordem: int