from sqlalchemy import create_engine, String, Integer, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, date

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__= "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    senha: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(50), default="aluno")
    professor: Mapped["Professor"] = relationship(back_populates="user", uselist=False)
    aluno: Mapped["Aluno"] = relationship(back_populates="user", uselist=False)
    foto: Mapped[str | None] = mapped_column(String(255), nullable=True)

class Professor(Base):
    __tablename__="professores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="professor")
    fichas: Mapped[list["Ficha"]] = relationship(back_populates="professor")
    nome: Mapped[str] = mapped_column(String(150))
    telefone: Mapped[str] = mapped_column(String(20))
 
class Aluno(Base):
    __tablename__="alunos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="aluno")
    fichas: Mapped[list["Ficha"]] = relationship(back_populates="aluno")
    nome: Mapped[str] = mapped_column(String(150))
    data_nascimento: Mapped[date] = mapped_column(Date)
    telefone: Mapped[str] = mapped_column(String(20))
    historicos: Mapped[list["HistoricoExecucao"]] = relationship(back_populates="aluno")
    avaliacoes: Mapped[list["AvaliacaoFisica"]] = relationship(back_populates="aluno")

class Exercicio(Base):
    __tablename__="exercicios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    descricao: Mapped[str] = mapped_column(String(500))
    grupo_muscular: Mapped[str] = mapped_column(String(150))
    itens: Mapped[list["ItemFicha"]] = relationship(back_populates="exercicio")

class Ficha(Base):
    __tablename__="fichas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"))
    aluno: Mapped["Aluno"] = relationship(back_populates="fichas")
    professor_id: Mapped[int] = mapped_column(ForeignKey("professores.id"))
    professor: Mapped["Professor"] = relationship(back_populates="fichas")
    nome: Mapped[str] = mapped_column(String(150))
    data_criacao: Mapped[datetime] = mapped_column(DateTime)
    itens: Mapped[list["ItemFicha"]] = relationship(back_populates="ficha")

class ItemFicha(Base):
    __tablename__="itens_ficha"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ficha_id: Mapped[int] = mapped_column(ForeignKey("fichas.id"))
    ficha: Mapped["Ficha"] = relationship(back_populates="itens")
    exercicio_id: Mapped[int] = mapped_column(ForeignKey("exercicios.id"))
    exercicio: Mapped["Exercicio"] = relationship(back_populates="itens")
    series: Mapped[int] = mapped_column(Integer)
    repeticoes: Mapped[int] = mapped_column(Integer)
    carga: Mapped[float] = mapped_column(Float)
    descanso: Mapped[int] = mapped_column(Integer)
    historicos: Mapped[list["HistoricoExecucao"]] = relationship(back_populates="item_ficha")

class HistoricoExecucao(Base):
    __tablename__="historicos_execucao"
    id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    item_ficha_id: Mapped[int] = mapped_column(ForeignKey("itens_ficha.id"))
    item_ficha: Mapped["ItemFicha"] = relationship(back_populates="historicos")
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"))
    aluno: Mapped["Aluno"] = relationship(back_populates="historicos")
    data_execucao: Mapped[datetime] = mapped_column(DateTime)
    series_realizadas: Mapped[int] = mapped_column(Integer)  
    repeticoes_realizadas: Mapped[int] = mapped_column(Integer)
    carga_utilizada: Mapped[float] = mapped_column(Float)
    observacao: Mapped[str] = mapped_column(String(500))

class AvaliacaoFisica(Base):
    __tablename__="avaliacoes_fisicas"
    id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"))
    aluno: Mapped["Aluno"] = relationship(back_populates="avaliacoes")
    data_avaliacao: Mapped[datetime] = mapped_column(DateTime)
    peso: Mapped[float] = mapped_column(Float)
    altura: Mapped[float] = mapped_column(Float)
    percentual_gordura: Mapped[float] = mapped_column(Float)
    massa_muscular: Mapped[float] = mapped_column(Float)
    observacao: Mapped[str] = mapped_column(String(500))