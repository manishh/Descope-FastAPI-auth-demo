import sqlite3
from contextlib import contextmanager
import os
from pathlib import Path
import bcrypt

# For production, this will be an RDBMS like PostgreSQL or similar
DB_PATH = Path(__file__).parent.parent / "descope_demo.db"


def _hash_password(password: str) -> str:
    rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=rounds)
    ).decode("utf-8")


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# --- Schema ---

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT    NOT NULL,
                email    TEXT    NOT NULL UNIQUE,
                bio      TEXT,
                password_hash TEXT
            )
        """)
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(user_profiles)").fetchall()
        }
        if "password_hash" not in columns:
            conn.execute("ALTER TABLE user_profiles ADD COLUMN password_hash TEXT")


# --- Queries ---

def get_user_by_email(email: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM user_profiles WHERE email = ?", (email,)
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM user_profiles WHERE id = ?", (user_id,)
        ).fetchone()

# --- Seeding ---

DUMMY_USERS = [
    {
        "name": "Manish",
        "email": "manish@example.com",
        "bio": "Loves building stuff and writing.",
        "password": "password123",
    },
    {
        "name": "Jakkie",
        "email": "jakkie@example.com",
        "bio": "Managing many responsibilities",
        "password": "password123",
    },
    {
        "name": "Kirstin",
        "email": "kirstin@example.com",
        "bio": "Excellent editor",
        "password": "password123",
    },
]


def seed_users(users: list[dict] = DUMMY_USERS):
    """Insert users, silently skipping any that already exist."""
    users_to_insert = []
    for user in users:
        raw_password = user.get("password", "password123")
        users_to_insert.append(
            {
                "name": user["name"],
                "email": user["email"],
                "bio": user.get("bio"),
                "password_hash": _hash_password(raw_password),
            }
        )

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO user_profiles (name, email, bio, password_hash)
            VALUES (:name, :email, :bio, :password_hash)
            """,
            users_to_insert,
        )

# --- Entrypoint ---

if __name__ == "__main__":
    init_db()
    seed_users()
    print("DB initialised and seeded.")
    user = get_user_by_email("manish@example.com")
    print(dict(user))
