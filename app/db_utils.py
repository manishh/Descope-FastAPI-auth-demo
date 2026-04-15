import sqlite3
from contextlib import contextmanager
from pathlib import Path
from passlib.context import CryptContext

# For production, this will be an RDBMS like PostgreSQL or similar
DB_PATH = Path(__file__).parent.parent / "descope_demo.db"


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
                hashed_password TEXT NOT NULL
            )
        """)


# --- Queries ---

def get_user_by_email(email: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM user_profiles WHERE email = ?", (email,)
        ).fetchone()

# --- Seeding ---

# Manually added for hashing dummy user passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

DUMMY_USERS = [
    
    # ---------->>> Original (incorrect), hardcoded password hash for "password123" by Gemini Code Assist
    # {"name": "Manish",   "email": "manish@example.com",   "bio": "Loves building stuff and writing.", "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57OT697.t95O"}, # password123
    # {"name": "Jakkie",   "email": "jakkie@example.com",   "bio": "Managing many responsibilities", "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57OT697.t95O"},
    # {"name": "Kirstin",  "email": "kirstin@example.com",  "bio": "Excellent editor", "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57OT697.t95O"},

    # ---------->>> Manually corrected hashing code to ensure the password hash is valid and corresponds to "password123"    
    {"name": "Manish",   "email": "manish@example.com",   "bio": "Loves building stuff and writing.", "hashed_password": get_password_hash("password123")}, # password123
    {"name": "Jakkie",   "email": "jakkie@example.com",   "bio": "Managing many responsibilities", "hashed_password": get_password_hash("password123")},
    {"name": "Kirstin",  "email": "kirstin@example.com",  "bio": "Excellent editor", "hashed_password": get_password_hash("password123")},
]


def seed_users(users: list[dict] = DUMMY_USERS):
    """Insert users, silently skipping any that already exist."""
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO user_profiles (name, email, bio, hashed_password)
            VALUES (:name, :email, :bio, :hashed_password)
            """,
            users,
        )

# --- Entrypoint ---

if __name__ == "__main__":
    init_db()
    seed_users()
    print("DB initialised and seeded.")
    user = get_user_by_email("manish@example.com")
    print(dict(user))
