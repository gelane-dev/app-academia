from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

class UsuarioCriar(UsuarioBase):
    senha: str
    
class UsuarioResposta(UsuarioBase):
    id: int

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str