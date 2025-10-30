from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import os

# Создание подключения к SQLite базе данных
DATABASE_URL = "sqlite:///./glossary.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель термина для базы данных
class TermModel(Base):
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    definition = Column(Text, nullable=False)

# Pydantic модели для API
class Term(BaseModel):
    name: str
    definition: str

class TermUpdate(BaseModel):
    definition: str

class TermResponse(Term):
    id: int

    class Config:
        from_attributes = True

# Создание таблиц в базе данных и добавление начальных данных
def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже данные
        if db.query(TermModel).count() == 0:
            # Добавляем начальные термины
            initial_terms = [
                TermModel(name="MP", definition="MP (mini program) - мини-программа внутри хост-платформы"),
                TermModel(name="MiniApps", definition="Мини-приложения внутри хост-платформы"),
                TermModel(name="HTML", definition="HTML (язык разметки гипертекста) — это стандартный язык для создания и структурирования веб-страниц"),
                TermModel(name="js", definition="JS (JavaScript) — это язык программирования")
            ]
            for term in initial_terms:
                db.add(term)
            db.commit()
            print("База данных инициализирована начальными данными")
    finally:
        db.close()

init_database()

app = FastAPI(title="Глоссарий терминов ВКР",
              description="API для управления глоссарием терминов ВКР",
              version="1.0.0")

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/terms", response_model=List[TermResponse])
def get_all_terms(db: Session = Depends(get_db)):
    """Получить список всех терминов"""
    terms = db.query(TermModel).all()
    return terms

@app.get("/terms/{term_name}", response_model=TermResponse)
def get_term(term_name: str, db: Session = Depends(get_db)):
    """Получить информацию о конкретном термине"""
    term = db.query(TermModel).filter(TermModel.name == term_name).first()
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term

@app.post("/terms", response_model=TermResponse)
def create_term(term: Term, db: Session = Depends(get_db)):
    """Добавить новый термин"""
    # Проверяем, существует ли уже термин с таким именем
    existing_term = db.query(TermModel).filter(TermModel.name == term.name).first()
    if existing_term:
        raise HTTPException(status_code=400, detail="Термин уже существует")

    db_term = TermModel(name=term.name, definition=term.definition)
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term

@app.put("/terms/{term_name}", response_model=TermResponse)
def update_term(term_name: str, term_update: TermUpdate, db: Session = Depends(get_db)):
    """Обновить существующий термин"""
    term = db.query(TermModel).filter(TermModel.name == term_name).first()
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")

    term.definition = term_update.definition
    db.commit()
    db.refresh(term)
    return term

@app.delete("/terms/{term_name}")
def delete_term(term_name: str, db: Session = Depends(get_db)):
    """Удалить термин из глоссария"""
    term = db.query(TermModel).filter(TermModel.name == term_name).first()
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")

    db.delete(term)
    db.commit()
    return {"message": f"Термин '{term_name}' удален"}