from app.db_utils import init_db, seed_users

if __name__ == "__main__":
    init_db()
    seed_users()
    print("Initialized DB with dummy users successfully.")