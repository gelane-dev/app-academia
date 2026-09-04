from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..core.seguranca import verificar_professor, verificar_aluno
from ..schemas.ficha import FichaCriar, ItemFichaCriar, AtualizarFicha
from ..models import Aluno, Ficha, ItemFicha, Exercicio

router = APIRouter()

@router.post("/criarficha")
def criar_ficha(criar: FichaCriar, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    aluno = db.scalar(
        select(Aluno).where(Aluno.id == criar.aluno_id))

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )

    ficha = Ficha(
        aluno_id = aluno.id,
        professor_id = professor.id,
        nome = criar.nome,
        data_criacao = datetime.now()
    )
        
    db.add(ficha) 
    db.commit()
    db.refresh(ficha)

    return ficha

@router.post("/ficha/item")
def criar_itens_ficha(criar: ItemFichaCriar, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id  == criar.ficha_id))

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
    
    exercicio = select(Exercicio).where(Exercicio.id == criar.exercicio_id)
    
    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )

    item = ItemFicha(
        ficha_id = ficha.id,
        exercicio_id = criar.exercicio_id,
        series = criar.series,
        repeticoes = criar.repeticoes,
        carga = criar.carga,
        descanso = criar.descanso
    )
        
    db.add(item)
    db.commit()
    db.refresh(item)

    return item

@router.get("/ficha/{id}", response_model=FichaResposta)
def ficha_aluno(id: int, aluno=Depends(verificar_aluno), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id == id))

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )
    
    if ficha.aluno_id != aluno.id:
         raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )

    return ficha

@router.put("/ficha/atualizar/{id}", response_model=FichaResposta)
def atualizar_nome(id: int, ficha: AtualizarFicha, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id == id))

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )
    
    if ficha.aluno_id != aluno.id:
         raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )

    ficha.nome = ficha.nome

    db.commit()

    return {"mensagem": "nome atualizado"}