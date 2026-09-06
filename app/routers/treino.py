from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.seguranca import verificar_professor
from ..schemas.treino import TreinoCriar, TreinoResposta, AtualizarTreino
from ..models import Ficha, Treino

router = APIRouter()

@router.post("/treino")
def criar_treino(dados: TreinoCriar, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id  == dados.ficha_id, Ficha.ativo.is_(True)))

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )
    
    if ficha.professor_id != professor.id:
        raise HTTPException(
            status_code=403,
            detail="Você não é o professor responsável por esta ficha"
        )
    
    treino = Treino(
    ficha_id = dados.ficha_id,
    nome = dados.nome,
    dia_semana = dados.dia_semana,
    ordem = dados.ordem,
    ativo=True
)
        
    db.add(treino)
    db.commit()
    db.refresh(treino)

    return treino

@router.get("/treino/ficha/{ficha_id}", response_model=list[TreinoResposta])
def listar_treinos(ficha_id: int, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    ficha = db.scalar(select(Ficha).where(Ficha.id == ficha_id, Ficha.ativo.is_(True)))

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Você não tem ficha salva"
        )
    
    if ficha.professor_id != professor.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para visualizar os treinos desta ficha"
        )
    
    treinos = db.scalars(
     select(Treino).where(Treino.ficha_id == ficha_id, Treino.ativo.is_(True)).order_by(Treino.ordem)).all()
    
    if not treinos:
        raise HTTPException(
            status_code=404,
            detail="Você não tem treinos salvos"
        )
    
    return treinos

@router.put("/treino/{id}", response_model=TreinoResposta)
def atualizar_treino(id: int, dados: AtualizarTreino, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    treino = db.scalar(
        select(Treino).where(Treino.id == id, Treino.ativo.is_(True)))

    if not treino:
        raise HTTPException(
            status_code=404,
            detail="Treino não encontrado"
        )

    ficha = db.scalar(
        select(Ficha).where(Ficha.id == treino.ficha_id, Ficha.ativo.is_(True)))
    
    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )

    if ficha.professor_id != professor.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para alterar esta ficha de treino"
        )

    treino.nome = dados.nome
    treino.dia_semana = dados.dia_semana
    treino.ordem = dados.ordem

    db.commit()
    db.refresh(treino)
    
    return treino

@router.delete("/treino/{id}")
def deletar_treino(id: int, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    treino = db.scalar(
        select(Treino).where(Treino.id == id, Treino.ativo.is_(True)))

    if not treino:
        raise HTTPException(
            status_code=404,
            detail="Treino não encontrado"
        )
    
    ficha = db.scalar(
        select(Ficha).where(Ficha.id == treino.ficha_id))
    
    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )   

    if ficha.professor_id != professor.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para excluir este treino"
        )

    treino.ativo = False

    db.commit()

    return {"mensagem": "Treino excluído com sucesso"}