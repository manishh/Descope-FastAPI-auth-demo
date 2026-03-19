import sqlite3
from contextlib import contextmanager
from pathlib import Path

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
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                bio           TEXT,
                password_hash TEXT
            )
        """)
        # Migrate existing DBs that pre-date the password_hash column.
        try:
            conn.execute("ALTER TABLE user_profiles ADD COLUMN password_hash TEXT")
        except Exception:
            pass  # Column already exists


# --- Queries ---

def get_user_by_email(email: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM user_profiles WHERE email = ?", (email,)
        ).fetchone()


# --- Seeding ---

DUMMY_USERS = [
    {"name": "Manish",  "email": "manish@example.com",  "bio": "Loves building stuff and writing."},
    {"name": "Jakkie",  "email": "jakkie@example.com",  "bio": "Managing many responsibilities"},
    {"name": "Kirstin", "email": "kirstin@example.com", "bio": "Excellent editor"},
]


def seed_users(users: list[dict] | None = None):
    """Insert users, silently skipping any that already exist.

    Each dict must contain name, email, bio, and password_hash.
    When *users* is omitted the DUMMY_USERS are seeded with a default password.
    """
    if users is None:
        from app.auth import hash_password  # local import avoids circular dep at load time
        users = [{**u, "password_hash": hash_password("password123")} for u in DUMMY_USERS]

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO user_profiles (name, email, bio, password_hash)
            VALUES (:name, :email, :bio, :password_hash)
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
