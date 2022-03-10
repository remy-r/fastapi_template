from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from alembic.config import Config
from alembic import command


import databases
import sqlalchemy
import logging
from security_service import (
    User,
    UserIn,
    UserInDB,
    Token,
    TokenData,
    SecurityService,
)


logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./test.db"

security_service = SecurityService(DATABASE_URL)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

notes = sqlalchemy.Table("notes", metadata, autoload_with=engine)


app = FastAPI()


class NoteIn(BaseModel):
    text: str
    text2: Optional[str]
    completed: bool


class Note(BaseModel):
    id: int
    text: str
    text2: Optional[str]
    completed: bool


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/notes/", response_model=List[Note], tags=["notes"])
async def read_notes(current_user: User = Depends(security_service.get_current_user)):
    query = notes.select()
    return await database.fetch_all(query)


@app.put("/notes/", response_model=Note, tags=["notes"])
async def create_note(
    note: NoteIn, current_user: User = Depends(security_service.get_current_user)
):
    query = notes.insert().values(
        text=note.text, completed=note.completed, text2=note.text2
    )
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}


@app.post("/token", response_model=Token, tags=["account"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await security_service.service_login_for_access_token(form_data)


@app.get("/users/me", tags=["account"])
async def read_users_me(
    current_user: User = Depends(security_service.get_current_user),
):
    return current_user


@app.get("/users/", response_model=List[User], tags=["account"])
async def list_users(current_user: User = Depends(security_service.get_current_user)):
    query = security_service.users.select()
    return await security_service.database.fetch_all(query)


@app.put("/users/create", response_model=UserInDB, tags=["account"])
async def create_user(
    user: UserIn, current_user: User = Depends(security_service.get_current_user)
):
    return await security_service.service_create_user(user, current_user)


@app.delete("/users/delete/{item_id}", tags=["account"])
async def delete_user(
    item_id: int, current_user: User = Depends(security_service.get_current_user)
):
    query = security_service.users.delete().where(
        security_service.users.c.id == item_id
    )
    last_record_id = await security_service.database.execute(query)
    return {"data": last_record_id}
