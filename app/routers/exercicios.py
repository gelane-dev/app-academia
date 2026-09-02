from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.exercicio import ExercicioCriar, ExercicioAtualizar, ExercicioResposta
from ..models import Exercicio
from ..core.seguranca import verificar_professor

router = APIRouter()


@router.post("/exercicios", response_model=ExercicioResposta)
def cria_exercicio(dados: ExercicioCriar, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = Exercicio(
        nome=dados.nome,
        descricao=dados.descricao,
        grupo_muscular=dados.grupo_muscular
    )

    db.add(exercicio)
    db.commit()
    db.refresh(exercicio)

    return exercicio


@router.get("/exercicios", response_model=list[ExercicioResposta])
def listar_exercicios(db: Session = Depends(get_db)):

    exercicios = db.scalars(
        select(Exercicio)).all()

    return exercicios


@router.get("/exercicios/{id}", response_model=ExercicioResposta)
def lista_exercicio(id: int, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = db.scalar(
        select(Exercicio).where(id == Exercicio.id))

    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )

    return exercicio


@router.put("/exercicios/{id}", response_model=ExercicioResposta)
def atualizar_exercicio(id: int, dados: ExercicioAtualizar, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = db.scalar(
        select(Exercicio).where(Exercicio.id == id))

    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )

    exercicio.nome = dados.nome
    exercicio.descricao = dados.descricao
    exercicio.grupo_muscular = dados.grupo_muscular

    db.commit()
    db.refresh(exercicio)

    return exercicio


@router.delete("/exercicios/{id}")
def deletar_exercicio(id: int, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = db.scalar(
        select(Exercicio).where(Exercicio.id == id))

    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )

    db.delete(exercicio)
    db.commit()

    return {"mensagem": "exercício deletado com sucesso"}
