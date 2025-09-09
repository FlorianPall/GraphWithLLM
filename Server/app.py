from flask import Flask, render_template, request, jsonify, Response
import os
import json
import time
import threading
from datetime import datetime
from queue import Queue
import uuid
from werkzeug.utils import secure_filename

from Helper.Files import config
from Helper import csvFile
from Pdf import pdfFile
import Startup
from Graph import Graph, ESCO, MergeGraphs
app = Flask(__name__)

# Konfiguration für File-Upload
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max file size
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Storage für Drawer-Daten und Log-Queues
drawer_data = {}
log_queues = {}
running_processes = {}
uploaded_files = {}  # Neue Speicherung für hochgeladene Dateien
ai_data = None

drawers = {
    1: 'ESCO-Datenbank',
    2: 'PDF-Extraktion',
    3: 'Graph-Erstellung',
    4: 'ESCO-Labels',
    5: 'Graph-Zusammenführung',
    6: 'ESCO-Verknüpfung',
    7: 'Cipher-Erstellung'
}

drawer_file_mapping = {
    1: None,
    2: 'Pdf_JSON',
    3: 'Graph_JSON',
    4: None,
    5: 'Merged_Graph_JSON',
    6: 'Merged_Graph_ESCO_JSON',
    7: 'LLM_Graph'
}

# Initialisiere Standard-Daten für alle 7 Drawer
for i in range(1, 8):
    drawer_data[i] = {
        'text': 'Placeholder',
        'logs': []
    }
    log_queues[i] = Queue()
    running_processes[i] = {'status': 'idle', 'process_id': None}
    uploaded_files[i] = []  # Liste der hochgeladenen Dateien pro Drawer


@app.route('/')
def index():
    Startup.folder_structure()
    return render_template('index.html', drawer_count=7, drawers=drawers)


@app.route('/folder/all', methods=['GET'])
def all_folders():
    try:
        cache_dir = config('Caching', print, '..')['Cache_Directory']
        folders = os.listdir('../' + cache_dir)
        folders.sort()
        folders += ["Neuen Ordner erstellen"]
        return jsonify({'success': True, 'folders': folders})
    except:
        return jsonify({'success': False, 'message': 'Fehler beim Abrufen der Ordnerliste'})


@app.route('/folder/create', methods=['POST'])
def create_folder():
    """Route zum Erstellen eines neuen Ordners"""
    try:
        data = request.get_json()
        folder_name = data.get('folder_name', '').strip()

        if not folder_name:
            return jsonify({'success': False, 'message': 'Ordnername ist erforderlich'})

        # Überprüfe auf ungültige Zeichen
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in folder_name for char in invalid_chars):
            return jsonify({'success': False, 'message': 'Ordnername enthält ungültige Zeichen'})

        cache_dir = config('Caching', print, '..')['Cache_Directory']
        full_path = '..' + os.path.join('..', cache_dir, folder_name)

        # Überprüfe ob Ordner bereits existiert
        if os.path.exists(full_path):
            return jsonify({'success': False, 'message': 'Ordner existiert bereits'})

        # Erstelle Ordner
        os.makedirs(full_path, exist_ok=True)

        return jsonify({
            'success': True,
            'message': f'Ordner "{folder_name}" wurde erfolgreich erstellt',
            'folder_name': folder_name
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Fehler beim Erstellen des Ordners: {str(e)}'})

@app.route('/folder/load', methods=['POST'])
def load_folder():
    data = request.get_json()
    folder_name = data.get('folder_name', '').strip()
    if not folder_name:
        return jsonify({'success': False, 'message': 'Ordnername ist erforderlich'})
    cache_dir = config('Caching', print, '..')['Cache_Directory']
    full_path = '..' + os.path.join('..', cache_dir, folder_name)
    if not os.path.exists(full_path):
        return jsonify({'success': False, 'message': 'Ordner existiert nicht'})
    for mapping in drawer_file_mapping.values():
        if mapping:
            file_path = os.path.join(full_path, config('Caching', print, '..')[mapping])
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = f.read()
                        drawer_id = list(drawer_file_mapping.keys())[list(drawer_file_mapping.values()).index(mapping)]
                        drawer_data[drawer_id]['text'] = data
                except Exception as e:
                    return jsonify({'success': False, 'message': f'Fehler beim Laden der Datei {mapping}.json: {str(e)}'})
            else:
                drawer_id = list(drawer_file_mapping.keys())[list(drawer_file_mapping.values()).index(mapping)]
                drawer_data[drawer_id]['text'] = f'Keine gespeicherte Datei für Drawer {drawer_id} gefunden.'
    uploaded_files[2] = []
    for file in os.listdir(full_path + '/uploads') if os.path.exists(full_path + '/uploads') else []:
        file_path = os.path.join(full_path, 'uploads', file)
        if os.path.isfile(file_path):
            file_info = {
                'original_name': file,
                'filepath': file_path,
                'size': os.path.getsize(file_path),
                'upload_time': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            }
            if file_info not in uploaded_files[2]:
                uploaded_files[2].append(file_info)
    return jsonify({
        'success': True,
        'message': f'Ordner "{folder_name}" wurde erfolgreich geladen'
    })

@app.route('/upload_file/<int:drawer_id>/<string:folder>', methods=['POST'])
def upload_file(drawer_id, folder):
    """Route zum Hochladen von Dateien für einen spezifischen Drawer"""
    if drawer_id not in drawer_data:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Keine Datei ausgewählt'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'Keine Datei ausgewählt'})

    if file and allowed_file(file.filename):
        try:
            # Sichere den Dateinamen
            filename = secure_filename(file.filename)

            # Erstelle Upload-Verzeichnis falls nicht vorhanden
            upload_dir = f'..{config('Caching', print,'..')['Cache_Directory']}/{folder}/uploads'
            os.makedirs(upload_dir, exist_ok=True)

            # Speichere die Datei
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)

            # Füge Datei-Info zur Liste hinzu
            file_info = {
                'original_name': file.filename,
                'filepath': filepath,
                'size': os.path.getsize(filepath),
                'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            uploaded_files[drawer_id].append(file_info)

            # Log-Eintrag hinzufügen
            timestamp_log = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp_log}] Datei '{file.filename}' hochgeladen ({file_info['size']} Bytes)"
            drawer_data[drawer_id]['logs'].append(log_entry)
            log_queues[drawer_id].put(log_entry)

            return jsonify({
                'success': True,
                'message': f'Datei "{file.filename}" erfolgreich hochgeladen',
                'file_info': file_info
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'Fehler beim Hochladen: {str(e)}'})

    return jsonify({'success': False, 'message': 'Dateityp nicht erlaubt'})


@app.route('/get_uploaded_files/<int:drawer_id>')
def get_uploaded_files(drawer_id):
    """Route zum Abrufen der hochgeladenen Dateien eines Drawers"""
    if drawer_id not in uploaded_files:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    return jsonify({
        'success': True,
        'files': uploaded_files[drawer_id]
    })


@app.route('/delete_uploaded_file/<int:drawer_id>/<int:file_index>', methods=['DELETE'])
def delete_uploaded_file(drawer_id, file_index):
    """Route zum Löschen einer hochgeladenen Datei"""
    if drawer_id not in uploaded_files:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    if file_index >= len(uploaded_files[drawer_id]):
        return jsonify({'success': False, 'message': 'Datei nicht gefunden'})

    try:
        file_info = uploaded_files[drawer_id][file_index]

        # Lösche physische Datei
        if os.path.exists(file_info['filepath']):
            os.remove(file_info['filepath'])

        # Entferne aus Liste
        uploaded_files[drawer_id].pop(file_index)

        # Log-Eintrag hinzufügen
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] Datei '{file_info['original_name']}' gelöscht"
        drawer_data[drawer_id]['logs'].append(log_entry)
        log_queues[drawer_id].put(log_entry)

        return jsonify({
            'success': True,
            'message': f'Datei "{file_info["original_name"]}" gelöscht'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Fehler beim Löschen: {str(e)}'})


@app.route('/start_drawer/<int:drawer_id>/<string:cache_folder>', methods=['POST'])
def start_drawer(drawer_id, cache_folder):
    """Route zum Starten eines Drawers mit Background-Prozess"""
    global ai_data
    if drawer_id not in drawer_data:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    if cache_folder == '' or cache_folder == 'Neuen Ordner erstellen' or cache_folder == 'empty':
        return jsonify({'success': False, 'message': 'Cache-Ordner ist erforderlich'})

    # Prüfe ob bereits ein Prozess läuft
    for drawer in running_processes:
        if running_processes[drawer]['status'] == 'running':
            return jsonify({
                'success': False,
                'message': f'Drawer {drawer} läuft bereits!'
            })

    def log_callback(message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        drawer_data[drawer_id]['logs'].append(log_entry)
        log_queues[drawer_id].put(log_entry)
    def set_process_complete(return_data):
        global ai_data
        running_processes[drawer_id]['status'] = 'completed'
        log_callback(f"Prozess abgeschlossen")
        ai_data = return_data
        cache_dir = config('Caching', print, '..')['Cache_Directory']
        full_path = '..' + os.path.join('..', cache_dir, cache_folder)
        file_path = os.path.join(full_path, config('Caching', print, '..')[drawer_file_mapping[drawer_id]])
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = f.read()
                    drawer_data[drawer_id]['text'] = file_data
            except Exception as e:
                return jsonify({'success': False, 'message': f'Fehler beim Laden der Datei: {str(e)}'})
        else:
            drawer_data[drawer_id]['text'] = f'Keine gespeicherte Datei für Drawer {drawer_id} gefunden.'
            return jsonify({'success': False, 'message': f'Keine gespeicherte Datei für Drawer {drawer_id} gefunden.'})
    def set_process_error():
        running_processes[drawer_id]['status'] = 'error'
        log_callback(f"Prozess mit Fehler beendet")

    # Starte neuen Prozess
    process_id = str(uuid.uuid4())
    running_processes[drawer_id]['status'] = 'running'
    running_processes[drawer_id]['process_id'] = process_id

    if drawer_id == 1:
        # Starte Background-Thread
        thread = threading.Thread(
            target=csvFile.csv_to_db,
            args=(cache_folder, log_callback, set_process_complete, set_process_error)
        )
        thread.daemon = True
        thread.start()
    elif drawer_id == 2:
        data = request.get_json()
        args = data.get('args', '').strip()
        if not args:
            running_processes[drawer_id]['status'] = 'error'
            return jsonify({'success': False, 'message': 'Datei auswählen ist erforderlich'})
        # Starte Background-Thread
        thread = threading.Thread(
            target=pdfFile.extract_pdf,
            args=(args, cache_folder, ai_data, log_callback, set_process_complete, set_process_error)
        )
        thread.daemon = True
        thread.start()
    elif drawer_id == 3:
        # Starte Background-Thread
        thread = threading.Thread(
            target=Graph.create_json_graph,
            args=(ai_data, cache_folder, log_callback, set_process_complete, set_process_error)
        )
        thread.daemon = True
        thread.start()
    elif drawer_id == 4:
        # Starte Background-Thread
        thread = threading.Thread(
            target=csvFile.export_preferred_label,
            args=(cache_folder, log_callback, set_process_complete, set_process_error)
        )
        thread.daemon = True
        thread.start()
    elif drawer_id == 5:
        # Starte Background-Thread
        thread = threading.Thread(
            target=MergeGraphs.merge,
            args=(cache_folder, log_callback, set_process_complete, set_process_error)
        )
        thread.daemon = True
        thread.start()
    elif drawer_id == 6:
        # Starte Background-Thread
        thread = threading.Thread(
            target=ESCO.connect_esco,
            args=(ai_data, cache_folder, log_callback, set_process_complete, set_process_error)
        )
        thread.daemon = True
        thread.start()
    elif drawer_id == 7:
        # Starte Background-Thread
        thread = threading.Thread(
            target=Graph.create_cipher_graph,
            args=(ai_data, cache_folder, log_callback, set_process_complete, set_process_error)
        )
        thread.daemon = True
        thread.start()
    else:
        running_processes[drawer_id]['status'] = 'error'
        return jsonify({'success': False, 'message': 'Drawer nicht implementiert'})

    return jsonify({
        'success': True,
        'message': f'Drawer {drawer_id} Prozess gestartet',
        'process_id': process_id,
        'status': 'running'
    })




@app.route('/drawer_status/<int:drawer_id>')
def drawer_status(drawer_id):
    """Aktuelle Status eines Drawers abrufen"""
    if drawer_id not in running_processes:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    return jsonify({
        'success': True,
        'status': running_processes[drawer_id]['status'],
        'process_id': running_processes[drawer_id]['process_id']
    })


@app.route('/logs_stream/<int:drawer_id>')
def logs_stream(drawer_id):
    """Server-Sent Events Stream für Live-Logs"""

    def generate():
        while True:
            try:
                # Warte auf neue Log-Einträge
                if not log_queues[drawer_id].empty():
                    log_entry = log_queues[drawer_id].get_nowait()
                    yield f"data: {json.dumps({'log': log_entry})}\n\n"
                else:
                    # Heartbeat alle 5 Sekunden
                    yield f"data: {json.dumps({'heartbeat': True})}\n\n"
                    time.sleep(5)
            except:
                break

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache'})


@app.route('/save_text/<int:drawer_id>', methods=['POST'])
def save_text(drawer_id):
    """Route zum Speichern des Textes"""
    if drawer_id not in drawer_data:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    data = request.get_json()
    text = data.get('text', '')

    drawer_data[drawer_id]['text'] = text

    # Log-Eintrag hinzufügen
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] Text in Drawer {drawer_id} gespeichert"
    drawer_data[drawer_id]['logs'].append(log_entry)
    log_queues[drawer_id].put(log_entry)

    return jsonify({
        'success': True,
        'message': 'Text erfolgreich gespeichert'
    })


@app.route('/reset_text/<int:drawer_id>', methods=['POST'])
def reset_text(drawer_id):
    """Route zum Zurücksetzen des Textes"""
    if drawer_id not in drawer_data:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    # Text auf Standard zurücksetzen
    drawer_data[drawer_id][
        'text'] = f'Standard Text für Drawer {drawer_id}\nHier können Sie Ihren Text eingeben und bearbeiten.'

    # Log-Eintrag hinzufügen
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] Text in Drawer {drawer_id} zurückgesetzt"
    drawer_data[drawer_id]['logs'].append(log_entry)
    log_queues[drawer_id].put(log_entry)

    return jsonify({
        'success': True,
        'message': 'Text erfolgreich zurückgesetzt',
        'text': drawer_data[drawer_id]['text']
    })


@app.route('/get_drawer_data/<int:drawer_id>')
def get_drawer_data(drawer_id):
    """Route zum Abrufen der Drawer-Daten"""
    if drawer_id not in drawer_data:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    return jsonify({
        'success': True,
        'text': drawer_data[drawer_id]['text'],
        'logs': drawer_data[drawer_id]['logs'],
        'status': running_processes[drawer_id]['status'],
        'uploaded_files': uploaded_files[drawer_id]
    })


@app.route('/clear_logs/<int:drawer_id>', methods=['POST'])
def clear_logs(drawer_id):
    """Route zum Löschen der Logs"""
    if drawer_id not in drawer_data:
        return jsonify({'success': False, 'message': 'Drawer nicht gefunden'})

    drawer_data[drawer_id]['logs'] = []

    # Queue leeren
    while not log_queues[drawer_id].empty():
        log_queues[drawer_id].get_nowait()

    return jsonify({
        'success': True,
        'message': 'Logs gelöscht'
    })


# Templates-Ordner erstellen falls nicht vorhanden
if not os.path.exists('templates'):
    os.makedirs('templates')

# Uploads-Ordner erstellen falls nicht vorhanden
if not os.path.exists('uploads'):
    os.makedirs('uploads')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)