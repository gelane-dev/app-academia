from pydantic import BaseModel, EmailStr
from datetime import date

class UsuarioBase(BaseModel):
    email: EmailStr

class UsuarioCriar(UsuarioBase):
    senha: str
    
class UsuarioResposta(UsuarioBase):
    id: int

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class AlunoAtualizar(BaseModel):
    nome: str
    telefone: str
    data_nascimento: date

class ProfessorAtualizar(BaseModel):
    nome: str
    telefone: str