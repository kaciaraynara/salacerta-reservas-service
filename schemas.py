from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class LocalBase(BaseModel):
    nome: str
    endereco: str

class LocalCreate(LocalBase):
    pass

class LocalResponse(LocalBase):
    id: int

    class Config:
        from_attributes = True


class SalaBase(BaseModel):
    nome: str
    capacidade: int
    local_id: int

class SalaCreate(SalaBase):
    pass

class SalaResponse(SalaBase):
    id: int

    class Config:
        from_attributes = True


class ReservaBase(BaseModel):
    responsavel: str
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    sala_id: int
    cafe: bool = False
    quantidade_pessoas: Optional[int] = 0

    @field_validator('quantidade_pessoas')
    @classmethod
    def validar_quantidade_pessoas(cls, v: int, info):
        if info.data.get('cafe') and (v is None or v <= 0):
            raise ValueError("Se houver cafe, a quantidade de pessoas deve ser maior que zero.")
        return v

class ReservaCreate(ReservaBase):
    pass

class ReservaResponse(ReservaBase):
    id: int

    class Config:
        from_attributes = True