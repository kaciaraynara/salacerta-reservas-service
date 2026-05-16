from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Local(Base):
    __tablename__ = "locais"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    
    salas = relationship("Sala", back_populates="local")

class Sala(Base):
    __tablename__ = "salas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    local_id = Column(Integer, ForeignKey("locais.id"))
    
    local = relationship("Local", back_populates="salas")
    reservas = relationship("Reserva", back_populates="sala")

class Reserva(Base):
    __tablename__ = "reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    responsavel = Column(String, nullable=False)
    descricao = Column(String)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    cafe = Column(Boolean, default=False)
    quantidade_pessoas = Column(Integer, default=0)
    
    sala_id = Column(Integer, ForeignKey("salas.id"))
    sala = relationship("Sala", back_populates="reservas")