from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import get_db
from .schemas.usuario import UsuarioCriar, UsuarioResposta, UsuarioLogin
from .models import User
from .core.seguranca import criar_hash, verificar_senha, criar_token, verificar_token

app = FastAPI(
    title="Academia API",
    description="API gerenciamento de academia",
    version="1.0.0"
)

@app.post("/login")
def logar(dados: UsuarioLogin, db: Session = Depends(get_db)):

    usuario = db.scalar(
select(User).where(User.email == dados.email))
    
    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )
    if not verificar_senha(dados.senha,usuario.senha):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    token = criar_token(usuario.id)

    return {
    "access_token": token,
    "token_type": "bearer"
}   


@app.post("/cadastro", response_model=UsuarioResposta)
def criar_usuario(dados: UsuarioCriar, db: Session = Depends(get_db)):

    usuario = User(
        email=dados.email,
        senha=criar_hash(dados.senha)
    )

    usuario_existente = db.scalar(
select(User).where(User.email == dados.email))
    
    if usuario_existetente:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario

@app.get("/perfil", response_model=UsuarioResposta)
def meu_perfil(db: Session = Depends(get_db), verificar: dict = Depends(verificar_token)):

    id_usuario = int(verificar["sub"])
    
    usuario = db.scalar(
    select(User).where(User.id == id_usuario))

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuario não encontado"
        )
    
    return usuario