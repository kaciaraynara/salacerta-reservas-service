from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Driver pg8000 para evitar conflitos de Unicode no Windows
SQLALCHEMY_DATABASE_URL = "postgresql+pg8000://postgres:Lylu2904@localhost:5432/salacerta_reservas"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()