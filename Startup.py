import os


def folder_structure():
    necessary_folders = [
        './src/Cache',
        './src/ESCO',
        './src/Modules',
        './src/Output'
    ]
    for directory_path in necessary_folders:
        try:
            # Prüfen ob Verzeichnis existiert
            if not os.path.exists(directory_path):
                # Verzeichnis erstellen
                os.makedirs(directory_path)
                print(f"Verzeichnis erstellt: {directory_path}")
            else:
                print(f"Verzeichnis existiert bereits: {directory_path}")
        except Exception as e:
            print(f"Fehler beim Erstellen des Verzeichnisses: {e}")