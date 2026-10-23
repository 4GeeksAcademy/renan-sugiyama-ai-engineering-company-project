import hashlib
import os
import secrets
import sqlite3
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from .passwords import hash_password, verify_password

DATABASE_PATH = Path(
    os.environ.get("AUTH_DATABASE_PATH", Path(__file__).resolve().parents[1] / "data/auth.sqlite3")
)
SESSION_DURATION_SECONDS = 8 * 60 * 60
DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))
bearer = HTTPBearer(auto_error=False)


@contextmanager
def database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


@asynccontextmanager
async def lifespan(_application: FastAPI):
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with database() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at INTEGER NOT NULL
            );
        """)
    yield


app = FastAPI(title="Nexova Auth API", version="0.1.0", lifespan=lifespan)


class LoginCredentials(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1024)


class LoginSession(BaseModel):
    userId: str
    sessionId: str
    expiresAt: str
    token: str | None = None


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def session_response(user_id: str, session_id: str, expires_at: int, token: str | None = None):
    return LoginSession(
        userId=user_id,
        sessionId=session_id,
        expiresAt=datetime.fromtimestamp(expires_at, timezone.utc).isoformat(),
        token=token,
    )


@app.post("/login", response_model=LoginSession, response_model_exclude_none=True)
def login(
    response: Response,
    credentials: LoginCredentials | None = None,
    authorization: HTTPAuthorizationCredentials | None = Security(bearer),
):
    response.headers["Cache-Control"] = "no-store"
    now = int(time.time())
    with database() as connection:
        connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
        if authorization is not None:
            session = connection.execute(
                """SELECT sessions.*, users.active FROM sessions
                   JOIN users ON users.id = sessions.user_id
                   WHERE token_hash = ? AND expires_at > ? AND users.active = 1""",
                (token_hash(authorization.credentials), now),
            ).fetchone()
            if session is None:
                raise HTTPException(status_code=401, detail="Invalid or expired session")
            return session_response(session["user_id"], session["session_id"], session["expires_at"])

        if credentials is None:
            raise HTTPException(status_code=401, detail="Credentials required")
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?", (credentials.username,)
        ).fetchone()
        password_matches = verify_password(
            credentials.password, user["password_hash"] if user else DUMMY_PASSWORD_HASH
        )
        if not password_matches or user is None or not user["active"]:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = secrets.token_urlsafe(32)
        session_id = str(uuid4())
        expires_at = now + SESSION_DURATION_SECONDS
        connection.execute(
            "INSERT INTO sessions (token_hash, session_id, user_id, expires_at) VALUES (?, ?, ?, ?)",
            (token_hash(token), session_id, user["id"], expires_at),
        )
        return session_response(user["id"], session_id, expires_at, token)


@app.post("/logout", status_code=204)
def logout(authorization: HTTPAuthorizationCredentials | None = Security(bearer)):
    if authorization is not None:
        with database() as connection:
            connection.execute(
                "DELETE FROM sessions WHERE token_hash = ?", (token_hash(authorization.credentials),)
            )
    return Response(status_code=204, headers={"Cache-Control": "no-store"})