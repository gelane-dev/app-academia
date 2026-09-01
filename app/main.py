from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import get_db
from .schemas.usuario import UsuarioCriar, UsuarioResposta, UsuarioLogin, ProfessorAtualizar, AlunoAtualizar
from .models import User, Professor
from .core.seguranca import criar_hash, verificar_senha, criar_token, verificar_token, verificar_professor, verificar_aluno, verificar_admin
from .schemas.professor import ProfessorCriar
from .schemas.atualizar_usuario import UsuarioAtualizar
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
            detail="Usuario não encontrado"
        )
    
    return usuario

@app.put("/perfil/professor")
def perfil_professor(dados: ProfessorAtualizar, verificar: dict = Depends(verificar_token), db: Session = Depends(get_db),):

    id_usuario = int(verificar["sub"])
    
    usuario = db.scalar(
    select(User).where(User.id == id_usuario))

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario não encontrado"
        )
    
    if usuario.tipo != "professor":
        raise HTTPException(
            status_code=403,
            detail="Acesso permitido apenas para professores"
        )

    professor = db.scalar(
    select(Professor).where(Professor.user_id == id_usuario))
        
    if not professor:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor não encontrado"
        )

    professor.nome = dados.nome
    professor.telefone = dados.telefone
    
    db.commit()

    return {"mensagem":"Alterações feitas"}

@app.put("/perfil/aluno")
def perfil_aluno(dados: AlunoAtualizar, verificar: dict = Depends(verificar_token), db: Session = Depends(get_db),):
    
    id_usuario = int(verificar["sub"])
    
    usuario = db.scalar(
    select(User).where(User.id == id_usuario))

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario não encontrado"
        )

    if usuario.tipo != "aluno":
        raise HTTPException(
            status_code=403,
            detail="Acesso permitido apenas para alunos"
        )

    aluno = db.scalar(
    select(Aluno).where(Aluno.user_id == id_usuario))
        
    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Perfil de aluno não encontrado"
        )

    aluno.nome = dados.nome
    aluno.telefone = dados.telefone
    aluno.data_nascimento = dados.data_nascimento

    db.commit()

    return {"mensagem":"Alterações feitas"}

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
        telefone=dados.telefone 
        ) 
    
    db.add(professor) 
    db.commit() 
    db.refresh(professor) 
    
    return { "mensagem": "Professor criado com sucesso" }