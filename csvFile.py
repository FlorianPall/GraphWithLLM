import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import os

CSV_FILES_FOLDER = "./src/ESCO/"

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
    files = os.listdir(CSV_FILES_FOLDER)
    if files:
        truncate_table()
    for file in files:
        try:
            import_csv(CSV_FILES_FOLDER + file)
        except Exception as e:
            print(f"Programm mit Fehler beendet: {str(e)}")

def truncate_table():
    """Leert die Tabelle und setzt den ID-Counter zurück"""
    try:
        with engine.connect() as connection:
            connection.execute(text("TRUNCATE TABLE skills RESTART IDENTITY"))
            connection.commit()
        print("Tabelle erfolgreich geleert")
    except Exception as e:
        print(f"Fehler beim Leeren der Tabelle: {str(e)}")
        raise

def clean_data(df):
    """Bereinigt die Daten vor dem Import"""
    # Ersetze NaN durch None für SQL NULL
    df = df.replace({np.nan: None})

    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '').str.replace('"', '')

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
                  if_exists='append',
                  index=False,
                  chunksize=1000)

        print(f"Erfolgreich {len(df)} Datensätze importiert")

    except Exception as e:
        print(f"Fehler beim Import in File {file_path}: {str(e)}")
        raise

def export_preferred_label():
    """Exportiert die preferred_label Spalte der Datenbank in eine CSV Datei"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DISTINCT preferredlabel FROM skills"))
            df = pd.DataFrame(result.fetchall(), columns=['preferredlabel'])
            df.to_csv('./src/output/preferred_label.csv', index=False, header=False, sep=';')
            print("Export erfolgreich")
    except Exception as e:
        print(f"Fehler beim Export: {str(e)}")
        raise
