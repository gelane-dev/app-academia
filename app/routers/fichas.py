from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..core.seguranca import verificar_professor, verificar_aluno
from ..schemas.ficha import FichaCriar, ItemFichaCriar, AtualizarFicha, FichaResposta, AtualizarItemFicha, ExecucaoHistorico, HistoricoResposta
from ..models import Aluno, Ficha, ItemFicha, Exercicio

router = APIRouter()

@router.post("/ficha")
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
        data_criacao = datetime.now(),
        ativo=True
    )
        
    db.add(ficha) 
    db.commit()
    db.refresh(ficha)

    return ficha

@router.post("/ficha/itens")
def criar_itens_ficha(criar: ItemFichaCriar, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id  == criar.ficha_id, Ficha.ativo.is_(True)))

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
    
    exercicio = db.scalar(select(Exercicio).where(Exercicio.id == criar.exercicio_id))
    
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
        descanso = criar.descanso,
        ativo=True
    )
        
    db.add(item)
    db.commit()
    db.refresh(item)

    return item

@router.get("/ficha/{id}", response_model=FichaResposta)
def ficha_aluno(id: int, aluno=Depends(verificar_aluno), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id == id, Ficha.ativo.is_(True)))

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
    
    ativos = db.scalars(
        select(ItemFicha).where(ItemFicha.ficha_id == ficha.id, ItemFicha.ativo.is_(True))).all()

    ficha.itens = ativos

    return ficha

@router.put("/ficha/{id}", response_model=FichaResposta)
def atualizar_ficha(id: int, dados: AtualizarFicha, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id == id))

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha de treino não encontrada"
        )

    if ficha.professor_id != professor.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para alterar esta ficha de treino"
        )

    ficha.nome = dados.nome

    db.commit()
    db.refresh(ficha)

    return ficha

@router.put("/ficha/item/{id}", response_model=ItemFichaResposta)
def atualizar_itens_ficha(id: int, dados: AtualizarItemFicha, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    item_ficha = db.scalar(
        select(ItemFicha).where(ItemFicha.id == id, ItemFicha.ativo.is_(True)))

    if not item_ficha:
        raise HTTPException(
            status_code=404,
            detail="Item da ficha não encontrado"
        )

    ficha = db.scalar(
        select(Ficha).where(Ficha.id == item_ficha.ficha_id, Ficha.ativo.is_(True)))
    
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

    item_ficha.series = dados.series
    item_ficha.repeticoes = dados.repeticoes
    item_ficha.carga = dados.carga
    item_ficha.descanso = dados.descanso

    db.commit()
    db.refresh(item_ficha)

    return item_ficha

@router.delete("/ficha/item/{id}")
def deletar_item_ficha(id: int, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    item_ficha = db.scalar(
        select(ItemFicha).where(ItemFicha.id == id))

    if not item_ficha:
        raise HTTPException(
            status_code=404,
            detail="Item da ficha não encontrado"
        )
    
    ficha = db.scalar(
        select(Ficha).where(Ficha.id == item_ficha.ficha_id))
    
    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )   

    if ficha.professor_id != professor.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para excluir este item"
        )

    if item_ficha.historicos:
        item_ficha.ativo = False
    else:
        db.delete(item_ficha)
    
    db.commit()

    return {
        "mensagem": "Item da ficha excluído com sucesso"
    }

@router.delete("/ficha/{id}")
def deletar_ficha(id: int, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    ficha = db.scalar(
        select(Ficha).where(Ficha.id == id))

    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )

    if ficha.professor_id != professor.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para excluir esta ficha"
        )
        
    ficha.ativo = False
    db.commit()

    return {
        "mensagem": "Ficha excluída com sucesso"
    }

@router.get("/ficha/aluno", response_model=list[FichaResposta])
def fichas(aluno=Depends(verificar_aluno), db: Session = Depends(get_db)):

    fichas = db.scalars(
        select(Ficha).where(Ficha.aluno_id == aluno.id, Ficha.ativo.is_(True))).all()

    if not fichas:
        raise HTTPException(
            status_code=404,
            detail="Você não possui fichas de treino ativas"
        )
    
    return fichas
  
@router.post("/ficha/treino")
def treino_realizado(dados: ExecucaoHistorico, aluno=Depends(verificar_aluno), db: Session = Depends(get_db)):

    item_ficha = db.scalar(select(ItemFicha).where(ItemFicha.id == dados.item_ficha_id,
    ItemFicha.ativo.is_(True)))

    if not item_ficha:
        raise HTTPException(
            status_code=404,
            detail="Item da ficha não encontrado"
        )

    ficha = db.scalar(select(Ficha).where(Ficha.id == item_ficha.ficha_id, 
    Ficha.aluno_id == aluno.id, Ficha.ativo.is_(True)))
    
    if not ficha:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )

    registrar_treino = HistoricoExecucao(
        item_ficha_id=dados.item_ficha_id,
        aluno_id=aluno.id,
        carga_utilizada=dados.carga_utilizada,
        repeticoes_realizadas=dados.repeticoes_realizadas,
        series_realizadas=dados.series_realizadas,
        observacao=dados.observacao,
        data_execucao=dados.data_execucao
    )
    
    
    db.add(registrar_treino)
    db.commit()
    db.refresh(registrar_treino)

    return {"mensagem": "treino registrado com sucesso"}

@router.get("/ficha/progresso", response_model=list[FichaResposta])
def historico_progresso(aluno=Depends(verificar_aluno), db: Session = Depends(get_db)):

    fichas = db.scalars(
        select(HistoricoExecucao).where(HistoricoExecucao.aluno_id == aluno.id,)).all()

    if not fichas:
        raise HTTPException(
            status_code=404,
            detail="Você não possui fichas de treino ativas"
        )
    
    return fichas