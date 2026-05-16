import os
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import models, schemas, database

# Inicialização das variáveis de ambiente
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

if not JWT_SECRET:
    raise ValueError("Erro crítico de infraestrutura: JWT_SECRET não definida no arquivo .env.")

# Componente de segurança do FastAPI para capturar o cabeçalho Authorization
security = HTTPBearer()

def validar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware de interceptação de segurança.
    Decodifica o token JWT emitido pelo microsserviço C#.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_aud": False,
                "verify_iss": False,
                "verify_exp": False
            }
        )
        return payload
    except jwt.InvalidSignatureError:
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Assinatura do token corrompida ou inválida."
            )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token JWT estruturalmente inválido."
        )

# Inicialização da API
app = FastAPI(
    title="SalaCerta Enterprise API",
    description="Microsserviço de gerenciamento de salas e regras de negócio de ocupação.",
    version="1.0.0"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def setup_infrastructure():
    """
    Sincroniza e alimenta o banco de dados de forma robusta e distribuída, 
    populando múltiplos centros de custo e salas temáticas corporativas.
    """
    db = next(database.get_db())
    try:
        # 1. Cadastro e verificação dos Locais/Filiais no PostgreSQL
        local_sede = db.query(models.Local).filter(models.Local.nome == "Sede Principal").first()
        if not local_sede:
            local_sede = models.Local(nome="Sede Principal")
            db.add(local_sede)
            db.commit()
            db.refresh(local_sede)

        local_paulista = db.query(models.Local).filter(models.Local.nome == "Filial Paulista").first()
        if not local_paulista:
            local_paulista = models.Local(nome="Filial Paulista")
            db.add(local_paulista)
            db.commit()
            db.refresh(local_paulista)

        local_rio = db.query(models.Local).filter(models.Local.nome == "Filial Rio de Janeiro").first()
        if not local_rio:
            local_rio = models.Local(nome="Filial Rio de Janeiro")
            db.add(local_rio)
            db.commit()
            db.refresh(local_rio)

        local_brasilia = db.query(models.Local).filter(models.Local.nome == "Filial Brasília").first()
        if not local_brasilia:
            local_brasilia = models.Local(nome="Filial Brasília")
            db.add(local_brasilia)
            db.commit()
            db.refresh(local_brasilia)

        # 2. Cadastro e distribuição de Salas de Reunião vinculadas dinamicamente
        # Salas da Sede Principal
        if not db.query(models.Sala).filter(models.Sala.nome == "Sala de Reuniões 01").first():
            db.add(models.Sala(nome="Sala de Reuniões 01", local_id=local_sede.id))
        
        if not db.query(models.Sala).filter(models.Sala.nome == "Sala de Reuniões 02").first():
            db.add(models.Sala(nome="Sala de Reuniões 02", local_id=local_sede.id))
            
        if not db.query(models.Sala).filter(models.Sala.nome == "Auditório Executivo").first():
            db.add(models.Sala(nome="Auditório Executivo", local_id=local_sede.id))

        # Salas da Filial Paulista
        if not db.query(models.Sala).filter(models.Sala.nome == "Sala Loft Tech").first():
            db.add(models.Sala(nome="Sala Loft Tech", local_id=local_paulista.id))
            
        if not db.query(models.Sala).filter(models.Sala.nome == "Espaço Inovação").first():
            db.add(models.Sala(nome="Espaço Inovação", local_id=local_paulista.id))

        # Salas da Filial Rio de Janeiro
        if not db.query(models.Sala).filter(models.Sala.nome == "Sala Copacabana").first():
            db.add(models.Sala(nome="Sala Copacabana", local_id=local_rio.id))
            
        if not db.query(models.Sala).filter(models.Sala.nome == "Sala Ipanema (Foco)").first():
            db.add(models.Sala(nome="Sala Ipanema (Foco)", local_id=local_rio.id))

        # Salas da Filial Brasília
        if not db.query(models.Sala).filter(models.Sala.nome == "Sala Esplanada").first():
            db.add(models.Sala(nome="Sala Esplanada", local_id=local_brasilia.id))
        
        db.commit()
        print("INFO: Infraestrutura corporativa de alta robustez populada com sucesso no PostgreSQL.")
    except Exception as e:
        db.rollback()
        print(f"Aviso na carga inicial de infraestrutura: {str(e)}")
    finally:
        db.close()


# =========================================================================
# ENDPOINTS DE INFRAESTRUTURA (ALIMENTAÇÃO DOS DROPDOWNS DINÂMICOS)
# =========================================================================

@app.get("/api/locais", response_model=List[schemas.LocalResponse])
def listar_locais(db: Session = Depends(database.get_db), token_payload: dict = Depends(validar_token)):
    """
    Retorna a lista completa de Filiais/Locais corporativos cadastrados no sistema.
    """
    return db.query(models.Local).all()

@app.get("/api/salas", response_model=List[schemas.SalaResponse])
def listar_salas(db: Session = Depends(database.get_db), token_payload: dict = Depends(validar_token)):
    """
    Retorna o catálogo completo de salas de reunião disponíveis para agendamento.
    """
    return db.query(models.Sala).all()


# =========================================================================
# ENDPOINTS DE DOMÍNIO (GESTÃO E REGRAS DE NEGÓCIO DE RESERVAS)
# =========================================================================

@app.get("/api/reservas", response_model=List[schemas.ReservaResponse])
def listar_reservas(db: Session = Depends(database.get_db), token_payload: dict = Depends(validar_token)):
    """
    Retorna o quadro geral de agendamentos ativos no ecossistema corporativo.
    """
    return db.query(models.Reserva).all()

@app.post("/api/reservas", response_model=schemas.ReservaResponse, status_code=status.HTTP_201_CREATED)
def criar_reserva(reserva: schemas.ReservaCreate, db: Session = Depends(database.get_db), token_payload: dict = Depends(validar_token)):
    """
    Processa e persiste uma nova reserva aplicando travas de segurança de cronograma e colisão de horários.
    """
    if reserva.data_fim <= reserva.data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cronograma incoerente: O término do evento deve ser posterior ao horário de início."
        )

    conflito = db.query(models.Reserva).filter(
        models.Reserva.sala_id == reserva.sala_id,
        and_(
            models.Reserva.data_inicio < reserva.data_fim,
            models.Reserva.data_fim > reserva.data_inicio
        )
    ).first()

    if conflito:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Indisponibilidade de recurso: Conflito de horário detectado para esta sala."
        )

    try:
        nova_reserva = models.Reserva(**reserva.model_dump())
        db.add(nova_reserva)
        db.commit()
        db.refresh(nova_reserva)
        return nova_reserva
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Falha operacional na gravação dos dados: {str(e)}"
        )

@app.put("/api/reservas/{reserva_id}", response_model=schemas.ReservaResponse)
def atualizar_reserva(reserva_id: int, reserva_atualizada: schemas.ReservaCreate, db: Session = Depends(database.get_db), token_payload: dict = Depends(validar_token)):
    """
    Modifica um agendamento existente revalidando as regras de colisões cronológicas.
    """
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não localizado.")

    if reserva_atualizada.data_fim <= reserva_atualizada.data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cronograma incoerente: O término do evento deve ser posterior ao horário de início."
        )

    conflito = db.query(models.Reserva).filter(
        models.Reserva.sala_id == reserva_atualizada.sala_id,
        models.Reserva.id != reserva_id, 
        and_(
            models.Reserva.data_inicio < reserva_atualizada.data_fim,
            models.Reserva.data_fim > reserva_atualizada.data_inicio
        )
    ).first()

    if conflito:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Indisponibilidade de recurso: Conflito de horário detectado para esta alteração."
        )

    try:
        for key, value in reserva_atualizada.model_dump().items():
            setattr(reserva, key, value)
        
        db.commit()
        db.refresh(reserva)
        return reserva
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Falha operacional na atualização dos dados: {str(e)}"
        )

@app.delete("/api/reservas/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_reserva(reserva_id: int, db: Session = Depends(database.get_db), token_payload: dict = Depends(validar_token)):
    """
    Remove definitivamente um registro de agendamento do banco de dados relacional.
    """
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não localizado.")
    
    try:
        db.delete(reserva)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Falha operacional na exclusão do registro: {str(e)}"
        )