
import sqlalchemy
import databases

from fastapi import  FastAPI, Request
from decouple import config
from configparser import ConfigParser

config_file = "alembic.ini"
alembic_config = ConfigParser()
alembic_config.read(config_file)

DATABASE_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_SERVER')}:{config('DB_PORT')}/{config('DB_NAME')}s"
alembic_config.set("alembic", "sqlalchemy.url", DATABASE_URL)

with open(config_file, 'w') as configfile:
    alembic_config.write(configfile)


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

books = sqlalchemy.Table(
    "books",
    metadata, 
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
    sqlalchemy.Column("pages", sqlalchemy.Integer),
    # sqlalchemy.Column("reader_id", sqlalchemy.ForeignKey("readers.id"), nullable= False, index=True)
)

readers = sqlalchemy.Table(
    "readers",
    metadata, 
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String)
)


readers_books = sqlalchemy.Table(
    "readers_books",
    metadata, 
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("book_id", sqlalchemy.ForeignKey("books.id"), nullable=False, index=True),
    sqlalchemy.Column("reader_id", sqlalchemy.ForeignKey("readers.id"), nullable=False, index=True)
)
# engine = sqlalchemy.create_engine(DATABASE_URL)
# metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/books/")
async def get_all_books():
    query = books.select()
    return await database.fetch_all(query)

@app.post("/books/")
async def create_book(request: Request):
    data = await request.json()
    query = books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}


@app.post("/readers/")
async def create_reader(request: Request):
    data = await request.json()
    query = readers.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}

@app.get("/readers/")
async def get_all_books():
    query = readers.select()
    return await database.fetch_all(query)

@app.post("/read/")
async def create_read(request: Request):
    data = await request.json()
    query = readers_books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}