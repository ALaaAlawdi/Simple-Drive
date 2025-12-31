from sqlalchemy import create_engine

# Database URL from alembic.ini
DATABASE_URL = "postgresql+psycopg2://simple_drive_user:StrongPassword123@localhost:5432/simple_drive"

def test_connection():
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as connection:
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    test_connection()