from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

# ИМПОРТИРУЕМ CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

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

    # Связи, где термин является источником или целью
    relationships_from = relationship(
        "TermRelationshipModel",
        foreign_keys="TermRelationshipModel.from_term_id",
        back_populates="from_term",
        cascade="all, delete-orphan",
    )
    relationships_to = relationship(
        "TermRelationshipModel",
        foreign_keys="TermRelationshipModel.to_term_id",
        back_populates="to_term",
        cascade="all, delete-orphan",
    )

    @property
    def relations(self):
        """Исходящие связи термина (для сериализации в ответе)."""
        return self.relationships_from


class TermRelationshipModel(Base):
    __tablename__ = "term_relationships"

    id = Column(Integer, primary_key=True, index=True)
    from_term_id = Column(
        Integer, ForeignKey("terms.id", ondelete="CASCADE"), nullable=False
    )
    to_term_id = Column(
        Integer, ForeignKey("terms.id", ondelete="CASCADE"), nullable=False
    )
    relation_type = Column(String, nullable=False)

    from_term = relationship(
        "TermModel", foreign_keys=[from_term_id], back_populates="relationships_from"
    )
    to_term = relationship(
        "TermModel", foreign_keys=[to_term_id], back_populates="relationships_to"
    )

    @property
    def target_name(self):
        return self.to_term.name if self.to_term else None


# Pydantic модели для API
class Term(BaseModel):
    name: str
    definition: str


class TermUpdate(BaseModel):
    definition: str


class TermRelationCreate(BaseModel):
    target_name: str
    relation_type: str


class TermRelationResponse(BaseModel):
    relation_type: str
    target_name: str

    class Config:
        from_attributes = True


class TermResponse(Term):
    id: int
    relations: List[TermRelationResponse] = []

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
                TermModel(
                    name="Нативное приложение",
                    definition="Приложение, разработанное специально для конкретной мобильной операционной системы (iOS или Android) с использованием языков программирования, характерных для этой платформы",
                ),
                TermModel(
                    name="Суперприложение",
                    definition="Многофункциональная платформа, которая объединяет в себе множество сервисов и мини-приложений, позволяя пользователю решать большинство повседневных задач в одном месте",
                ),
                TermModel(
                    name="Мессенджер",
                    definition="Программа, приложение или веб-сервис для обмена сообщениями через Интернет в реальном времени",
                ),
                TermModel(
                    name="Телеграм",
                    definition="Кроссплатформенный мессенджер. Позволяет обмениваться сообщениями, файлами, совершать звонки, а также включает функции каналов, ботов и крупных групповых чатов",
                ),
                TermModel(
                    name="Социальная сеть",
                    definition="Онлайн-платформа, предназначенная для построения социальных отношений между людьми, у которых есть общие интересы, деятельность, связи в реальной жизни. Ключевые функции включают создание личного профиля, список друзей/подписчиков, новостную ленту, группы и обмен пользовательским контентом",
                ),
                TermModel(
                    name="Вконтакте",
                    definition="Российская социальная сеть и мультимедийная платформа, объединяющая функции для общения, потребления контента и развлечений",
                ),
                TermModel(
                    name="Веб-приложение",
                    definition="Клиент-серверное приложение, в котором клиентская часть работает в браузере пользователя",
                ),
                TermModel(
                    name="Веб-технологии",
                    definition="Набор стандартов, языков и технологий, используемых для создания и функционирования веб-сайтов и веб-приложений. Основные из них включают HTML (структура), CSS (оформление) и JavaScript (логика и интерактивность)",
                ),
                TermModel(
                    name="Мини-приложение",
                    definition="Легковесное приложение, работающее внутри хост-платформы. Не требует установки из официальных магазинов приложений, использует веб-технологии для разработки и предоставляет пользователю нативный опыт взаимодействия",
                ),
                TermModel(
                    name="PWA",
                    definition="Прогрессивное веб-приложение, построенное по современным стандартам, которое может работать офлайн и отправлять push-уведомления, сочетая в себе преимущества веба и нативных приложений",
                ),
                TermModel(
                    name="Хост-платформа",
                    definition="Основное приложение или экосистема, внутри которой запускается и функционирует мини-приложение",
                ),
                TermModel(
                    name="WebView",
                    definition="Компонент в нативном приложении, который действует как мини-браузер для отображения веб-контента",
                ),
                TermModel(
                    name="Iframe",
                    definition="HTML-элемент, который позволяет встраивать на страницу другой, полностью независимый HTML-документ",
                ),
                TermModel(
                    name="SDK",
                    definition="Комплект средств разработки, который помогает создавать приложения для конкретной платформы. Включает в себя библиотеки, документацию, примеры кода.",
                ),
                TermModel(
                    name="Производительность",
                    definition="Показатель эффективности",
                ),
                TermModel(
                    name="FP",
                    definition="Момент, когда браузер или WebView впервые отрисовывает любой визуальный элемент на экране",
                ),
                TermModel(
                    name="FMP",
                    definition="Момент, когда на экране отображается основной, полезный для пользователя контент",
                ),
                TermModel(
                    name="TTI",
                    definition="Время, за которое приложение загружается и становится полностью отзывчивым на действия пользователя",
                ),
                TermModel(
                    name="FPS",
                    definition="Количество кадров, отрисовываемых за секунду",
                ),
            ]
            for term in initial_terms:
                db.add(term)
            db.commit()

            # Добавляем связи между терминами
            initial_relations = [
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Суперприложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Нативное приложение")
                    .first()
                    .id,
                    relation_type="является альтернативой",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Суперприложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Хост-платформа")
                    .first()
                    .id,
                    relation_type="имеет",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Суперприложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Мини-приложение")
                    .first()
                    .id,
                    relation_type="имеет",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Телеграм")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Хост-платформа")
                    .first()
                    .id,
                    relation_type="является",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Телеграм")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Мессенджер")
                    .first()
                    .id,
                    relation_type="является",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Вконтакте")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Социальная сеть")
                    .first()
                    .id,
                    relation_type="является",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Вконтакте")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Хост-платформа")
                    .first()
                    .id,
                    relation_type="является",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Хост-платформа")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "SDK")
                    .first()
                    .id,
                    relation_type="имеет",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Мини-приложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Iframe")
                    .first()
                    .id,
                    relation_type="отображается в",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Мини-приложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "WebView")
                    .first()
                    .id,
                    relation_type="отображается в",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Мини-приложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "PWA")
                    .first()
                    .id,
                    relation_type="схожая концепция с",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Мини-приложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Веб-приложение")
                    .first()
                    .id,
                    relation_type="является",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "PWA")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Веб-приложение")
                    .first()
                    .id,
                    relation_type="является",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Веб-приложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Веб-технологии")
                    .first()
                    .id,
                    relation_type="использует",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Веб-приложение")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Производительность")
                    .first()
                    .id,
                    relation_type="характеризуется",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Производительность")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "FPS")
                    .first()
                    .id,
                    relation_type="включает",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Производительность")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "FP")
                    .first()
                    .id,
                    relation_type="включает",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Производительность")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "FMP")
                    .first()
                    .id,
                    relation_type="включает",
                ),
                TermRelationshipModel(
                    from_term_id=db.query(TermModel)
                    .filter(TermModel.name == "Производительность")
                    .first()
                    .id,
                    to_term_id=db.query(TermModel)
                    .filter(TermModel.name == "TTI")
                    .first()
                    .id,
                    relation_type="включает",
                ),
                # # MP связан с MiniApps как "синоним"
                # TermRelationshipModel(from_term_id=db.query(TermModel).filter(TermModel.name == "MP").first().id,
                #                     to_term_id=db.query(TermModel).filter(TermModel.name == "MiniApps").first().id,
                #                     relation_type="синоним"),
                # # MiniApps связан с MP как "синоним"
                # TermRelationshipModel(from_term_id=db.query(TermModel).filter(TermModel.name == "MiniApps").first().id,
                #                     to_term_id=db.query(TermModel).filter(TermModel.name == "MP").first().id,
                #                     relation_type="синоним"),
                # # HTML связан с js как "используется с"
                # TermRelationshipModel(from_term_id=db.query(TermModel).filter(TermModel.name == "HTML").first().id,
                #                     to_term_id=db.query(TermModel).filter(TermModel.name == "js").first().id,
                #                     relation_type="используется с"),
                # # js связан с HTML как "используется с"
                # TermRelationshipModel(from_term_id=db.query(TermModel).filter(TermModel.name == "js").first().id,
                #                     to_term_id=db.query(TermModel).filter(TermModel.name == "HTML").first().id,
                #                     relation_type="используется с"),
                # # MP связан с HTML как "технология веб-разработки"
                # TermRelationshipModel(from_term_id=db.query(TermModel).filter(TermModel.name == "MP").first().id,
                #                     to_term_id=db.query(TermModel).filter(TermModel.name == "HTML").first().id,
                #                     relation_type="технология веб-разработки"),
            ]

            for relation in initial_relations:
                db.add(relation)
            db.commit()

            print("База данных инициализирована начальными данными и связями")
    finally:
        db.close()


init_database()

app = FastAPI(
    title="Глоссарий терминов ВКР",
    description="API для управления глоссарием терминов ВКР",
    version="1.0.0",
)

# Настройка CORS для разрешения запросов с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:8080",
    ],  # Разрешаем ваш фронтенд
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)


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


@app.post("/terms/{term_name}/relations", response_model=List[TermRelationResponse])
def add_term_relation(
    term_name: str, relation: TermRelationCreate, db: Session = Depends(get_db)
):
    """Добавить семантическую связь между терминами"""
    from_term = db.query(TermModel).filter(TermModel.name == term_name).first()
    to_term = db.query(TermModel).filter(TermModel.name == relation.target_name).first()

    if not from_term or not to_term:
        raise HTTPException(status_code=404, detail="Один или оба термина не найдены")

    # Проверяем наличие такой же связи
    existing_relation = (
        db.query(TermRelationshipModel)
        .filter(
            TermRelationshipModel.from_term_id == from_term.id,
            TermRelationshipModel.to_term_id == to_term.id,
            TermRelationshipModel.relation_type == relation.relation_type,
        )
        .first()
    )
    if existing_relation:
        raise HTTPException(status_code=400, detail="Такая связь уже существует")

    db_relation = TermRelationshipModel(
        from_term_id=from_term.id,
        to_term_id=to_term.id,
        relation_type=relation.relation_type,
    )
    db.add(db_relation)
    db.commit()
    db.refresh(from_term)
    return from_term.relations


@app.get("/terms/{term_name}/relations", response_model=List[TermRelationResponse])
def get_term_relations(term_name: str, db: Session = Depends(get_db)):
    """Получить семантические связи для указанного термина"""
    term = db.query(TermModel).filter(TermModel.name == term_name).first()
    if not term:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term.relations


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

    # Удаляем все связи, где термин участвует
    db.query(TermRelationshipModel).filter(
        or_(
            TermRelationshipModel.from_term_id == term.id,
            TermRelationshipModel.to_term_id == term.id,
        )
    ).delete(synchronize_session=False)

    db.delete(term)
    db.commit()
    return {"message": f"Термин '{term_name}' удален"}
