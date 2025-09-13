from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv("./DB_Setup/.env")

# PostgreSQL Verbindungsdaten aus .env
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')

def get_engine():
    # PostgreSQL Verbindung erstellen
    db_url = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    return create_engine(db_url)