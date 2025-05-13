from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

from dotenv import load_dotenv
import os

load_dotenv(".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")  # SQL Server hostname/IP
DB_PORT = os.getenv("DB_PORT", "1433")  # Default SQL Server port is 1433
DB_NAME = os.getenv("DB_NAME")

ODBC_DRIVER = "ODBC Driver 18 for SQL Server"

# Format connection string with port
SERVER_PORT = f"{DB_SERVER},{DB_PORT}" if DB_PORT else DB_SERVER
# Adding TrustServerCertificate=yes to bypass SSL validation issues
DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{SERVER_PORT}/{DB_NAME}?driver={ODBC_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"


class HeroBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = Field(default=None, max_length=1000)


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    alter_ego: str | None = Field(default=None, max_length=100)


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    alter_ego: str = Field(max_length=100)


class HeroUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    alter_ego: str | None = Field(default=None, max_length=100)


connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def check_db_connection():
    try:
        with Session(engine) as session:
            statement = select(Hero).limit(1)
            results = session.exec(statement)
            if results:
                print("Database connection is working.")
    except Exception as e:
        raise Exception(f"Error connecting to the database: {e}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()


@app.on_event("startup")
def on_startup():
    check_db_connection()


@app.get("/")
def welcome():
    return {"message": "Welcome to the Heroes FastAPI SQLModel example!"}


@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep) -> Any:
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(
        select(Hero).order_by(Hero.id).offset(offset).limit(limit)  # type: ignore
    ).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
