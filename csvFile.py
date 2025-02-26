import pandas as pd
from sqlalchemy import text
import numpy as np
import os
from Files import csv, config
from DBEngine import get_engine

CSV_FILES_FOLDER = "./src/ESCO/"

# PostgreSQL Verbindung erstellen
engine = get_engine()


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

    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip() if df[col].notna().any() else df[col]

    return df

def import_csv(file_path):
    """Importiert CSV Daten in die PostgreSQL Datenbank"""
    try:
        # CSV einlesen
        df = csv(file_path)

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
            result = connection.execute(text("SELECT DISTINCT preferredlabel FROM skills where preferredlabel is not null"))
            df = pd.DataFrame(result.fetchall(), columns=['preferredlabel'])
            file_name = config('Caching')['ESCO_preferred_label']
            df.to_csv('./src/Output/' + file_name, index=False, header=True, sep=';')

            result = connection.execute(
                text("SELECT DISTINCT preferredlabel, description FROM skills where preferredlabel is not null"))
            df = pd.DataFrame(result.fetchall(), columns=['preferredlabel', 'description'])
            file_name = config('Caching')['ESCO_preferred_label_and_description']
            df.to_csv('./src/Output/' + file_name, index=False, header=True, sep=';')
            print("Export erfolgreich")
    except Exception as e:
        print(f"Fehler beim Export: {str(e)}")
        raise
