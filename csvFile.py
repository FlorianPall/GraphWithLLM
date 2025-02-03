import pandas as pd
from sqlalchemy import create_engine
import numpy as np

CSV_FILE = "./src/ESCO/skills_en.csv"

# PostgreSQL Verbindungsdaten
DB_USER = 'admin'
DB_PASS = 'adminGeheim123'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'esco'

# PostgreSQL Verbindung erstellen
db_url = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_url)


def csv_to_db():
    """Funktion zum Importieren der CSV Daten in die Datenbank"""
    try:
        import_csv(CSV_FILE)
    except Exception as e:
        print(f"Programm mit Fehler beendet: {str(e)}")


def clean_data(df):
    """Bereinigt die Daten vor dem Import"""
    # Ersetze NaN durch None für SQL NULL
    df = df.replace({np.nan: None})

    return df


def import_csv(file_path):
    """Importiert CSV Daten in die PostgreSQL Datenbank"""
    try:
        # CSV einlesen
        df = pd.read_csv(file_path,
                         encoding='utf-8',
                         # Verhindert, dass Pandas Kommas in Textfeldern als Trenner interpretiert
                         quotechar='"',
                         # Erlaubt Anführungszeichen in Textfeldern
                         escapechar='\\')

        # Daten bereinigen
        df = clean_data(df)

        # In Datenbank schreiben
        df.to_sql('skills',
                  engine,
                  if_exists='replace',
                  index=False,
                  chunksize=1000)

        print(f"Erfolgreich {len(df)} Datensätze importiert")

    except Exception as e:
        print(f"Fehler beim Import: {str(e)}")
        raise
