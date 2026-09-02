from .base import Base
from .user import User
from .professor import Professor
from .aluno import Aluno
from .exercicio import Exercicio
from .ficha import Ficha
from .item_ficha import ItemFicha
from .historico_execucao import HistoricoExecucao
from .avaliacao_fisica import AvaliacaoFisica

__all__ = [
    "Base",
    "User",
    "Professor",
    "Aluno",
    "Exercicio",
    "Ficha",
    "ItemFicha",
    "HistoricoExecucao",
    "AvaliacaoFisica",
]
