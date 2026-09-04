from pydantic import BaseModel
from datetime import datetime

class FichaCriar(BaseModel):
    aluno_id: int
    nome: str

class ItemFichaCriar(BaseModel):
    ficha_id: int
    exercicio_id: int
    series: int
    repeticoes: int
    carga: float
    descanso: int

class ItemFichaResposta(BaseModel):
    id: int
    ficha_id: int
    exercicio_id: int
    series: int
    repeticoes: int
    carga: float
    descanso: int


class FichaResposta(BaseModel):
    id: int
    nome: str
    data_criacao: datetime
    itens: list[ItemFichaResposta]

class AtualizarFicha(BaseModel):
    nome: str

class AtualizarItemFicha(BaseModel):
    series: int
    repeticoes: int
    carga: float
    descanso: int

class ExecucaoHistorico(BaseModel):
    item_ficha_id: int
    data_execucao: datetime
    series_realizadas: int
    repeticoes_realizadas: int
    carga_utilizada: float
    observacao: str
    
class HistoricoResposta(BaseModel):
    item_ficha_id: int
    data_execucao: datetime
    series_realizadas: int
    repeticoes_realizadas: int
    carga_utilizada: float
    observacao: str