from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import get_db
from .schemas.usuario import UsuarioCriar, UsuarioResposta, UsuarioLogin
from .models import User, Professor
from .core.seguranca import criar_hash, verificar_senha, criar_token, verificar_token, verificar_professor, verificar_aluno, verificar_admin
from .schemas.professor import ProfessorCriar

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
    
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario

@app.get("/perfil", response_model=UsuarioResposta)
def meu_perfil(verificar: dict = Depends(verificar_token), db: Session = Depends(get_db),):

    id_usuario = int(verificar["sub"])
    
    usuario = db.scalar(
    select(User).where(User.id == id_usuario))

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuario não encontado"
        )
    
    return usuario

@app.get("/professor")
def conta_professor(professor = Depends(verificar_professor)):

    return professor.id

@app.get("/aluno")
def conta_aluno(aluno = Depends(verificar_aluno)):
    return aluno.id

@app.post("/admin/professores")
def criar_professor(dados: ProfessorCriar, admin = Depends(verificar_admin), db: Session = Depends(get_db)):
    
    usuario_existente = db.scalar(
    select(User).where(User.email == dados.email))

    if usuario_existente: 
        raise HTTPException( 
            status_code=400, 
            detail="E-mail já cadastrado" 
        ) 
    
    usuario = User( email=dados.email, 
        senha=criar_hash(dados.senha), 
        tipo="professor" ) 
    
    db.add(usuario) 
    db.flush() 
    
    professor = Professor( 
        user_id=usuario.id, 
        nome=dados.nome, 
        telefone=dados.telefone ) 
    
    db.add(professor) 
    db.commit() 
    db.refresh(professor) 
    
    return { "mensagem": "Professor criado com sucesso" }