from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.exercicio import ExercicioCriar, ExercicioAtualizar, ExercicioResposta
from ..models import Exercicio
from ..core.seguranca import verificar_professor
from ..services.cloudinary import upload_imagem, upload_video, deletar_video, deletar_imagem
from pathlib import Path

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
        select(Exercicio).where(Exercicio.ativo.is_(True))).all()

    return exercicios


@router.get("/exercicios/{id}", response_model=ExercicioResposta)
def lista_exercicio(id: int, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = db.scalar(
        select(Exercicio).where(Exercicio.id == id).where(Exercicio.ativo.is_(True)))

    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )
    
    return exercicio


@router.put("/exercicios/{id}", response_model=ExercicioResposta)
def atualizar_exercicio(id: int, dados: ExercicioAtualizar, professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = db.scalar(
        select(Exercicio).where(Exercicio.id == id).where(Exercicio.ativo.is_(True)))

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
        select(Exercicio).where(Exercicio.id == id).where(Exercicio.ativo.is_(True)))

    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )

    if exercicio.imagem_public_id:
        deletar_imagem(exercicio.imagem_public_id)
        exercicio.imagem = None
        exercicio.imagem_public_id = None
    
    if exercicio.video_public_id:
        deletar_video(exercicio.video_public_id)
        exercicio.video = None
        exercicio.video_public_id = None
       
    exercicio.ativo = False
    
    db.commit()

    return {"mensagem": "exercício deletado com sucesso"}

@router.put("/exercicios/{id}/imagem")
async def colocar_imagem(id: int, arquivo: UploadFile = File(), professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = db.scalar(
        select(Exercicio).where(Exercicio.id == id).where(Exercicio.ativo.is_(True)))

    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )
    
    extensao = Path(arquivo.filename).suffix.lower()

    extensoes_permitidas = [".jpg", ".jpeg", ".png"]

    if extensao not in extensoes_permitidas:
        raise HTTPException(
            status_code=400,
            detail="Formato de imagem não permitido"
        )

    imagem_bytes = await arquivo.read()

    tamanho = len(imagem_bytes)

    if tamanho > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="A imagem deve ter no máximo 5 MB"
        )

    await arquivo.seek(0)
    
    if exercicio.imagem_public_id:
        deletar_imagem(exercicio.imagem_public_id)
    
    url, public_id = upload_imagem(arquivo)
    
    exercicio.imagem = url
    exercicio.imagem_public_id = public_id

    db.commit()
    db.refresh(exercicio)

    return  {"mensagem": "Imagem do exercício atualizada com sucesso"}

@router.put("/exercicios/{id}/video")
async def colocar_video(id: int, arquivo: UploadFile = File(), professor=Depends(verificar_professor), db: Session = Depends(get_db)):

    exercicio = db.scalar(
        select(Exercicio).where(Exercicio.id == id).where(Exercicio.ativo.is_(True)))

    if not exercicio:
        raise HTTPException(
            status_code=404,
            detail="Exercicio não encontrado"
        )

    if arquivo.content_type not in ["video/mp4", "video/webm", "video/quicktime"]:
        raise HTTPException(
            status_code=400,
            detail="Formato de vídeo não permitido"
    )

    video_bytes = await arquivo.read()

    tamanho = len(video_bytes)

    if tamanho > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="O vídeo deve ter no máximo 50 MB"
        )
    
    await arquivo.seek(0)
    
    if exercicio.video_public_id:
        deletar_video(exercicio.video_public_id)

    url, public_id = upload_video(arquivo)
    
    exercicio.video = url
    exercicio.video_public_id = public_id

    db.commit()
    db.refresh(exercicio)

    return  {"mensagem": "Video do exercício atualizada com sucesso"}
