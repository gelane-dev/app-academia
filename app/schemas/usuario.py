from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    email: EmailStr

class UsuarioCriar(UsuarioBase):
    senha: str
    
class UsuarioResposta(UsuarioBase):
    id: int

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str