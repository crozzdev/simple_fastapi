from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from dotenv import load_dotenv
import os

load_dotenv(".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")  # Default SQL Server port is 1433
DB_NAME = os.getenv("DB_NAME")

ODBC_DRIVER = "ODBC Driver 17 for SQL Server"

DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={ODBC_DRIVER.replace(' ', '+')}"


class HeroBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = None


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    alter_ego: Annotated[str, Field(max_length=100)]


class HeroPublic(HeroBase):
    id: int


class HeroCreate(HeroBase):
    alter_ego: str


class HeroUpdate(SQLModel):
    name: str | None = None
    age: int | None = None
    secret_name: Annotated[str, Field(max_length=100)]


connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def check_db_connection():
    try:
        with Session(engine) as session:
            statement = select(Hero).limit(1)
            results = session.exec(statement)
            if results:
                print(results.all())
                print("Database connection is working.")
    except Exception as e:
        raise Exception(f"Error connecting to the database: {e}")


check_db_connection()
