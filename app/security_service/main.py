from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy
import databases
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt


class UserIn(BaseModel):
    name: str
    email: str
    password: str


class User(BaseModel):
    id: int
    name: str
    email: str


class UserInDB(User):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# openssl rand -hex 32
SECRET_KEY = "2107c6a15a4baa61a56c0c77adfcd1433b299f2f42450cd75c822d760d67dcf7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class SecurityService:
    def __init__(self, db):
        self.database = databases.Database(db)
        self.metadata = sqlalchemy.MetaData()
        self.engine = sqlalchemy.create_engine(
            db, connect_args={"check_same_thread": False}
        )
        self.users = sqlalchemy.Table("users", self.metadata, autoload_with=self.engine)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_user(self, username: str):
        query = self.users.select(self.users.c.email == username)
        users_returned = await self.database.fetch_all(query)

        if len(users_returned) >= 1:
            return UserInDB(**users_returned[0])

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = await self.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def get_password_hash(
        self, password: str, current_user: User = Depends(get_current_user)
    ):
        return {"data": pwd_context.hash(password)}

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, username: str, password: str):
        user = await self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.password):
            return False
        return user

    async def service_login_for_access_token(self, form_data):
        user = await self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    async def service_create_user(
        self, user: UserIn, current_user: User = Depends(get_current_user)
    ):
        user.password = pwd_context.hash(user.password)
        query = self.users.insert().values(
            name=user.name, email=user.email, password=user.password
        )
        last_record_id = await self.database.execute(query)
        return {**user.dict(), "id": last_record_id}
