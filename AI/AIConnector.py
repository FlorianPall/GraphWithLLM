import os
import time
from datetime import datetime, timedelta
import anthropic
import re
import json
import uuid
from dotenv import load_dotenv
from Helper.Files import config

load_dotenv("./DB_Setup/.env")

# Globale Variable für Rate-Limiting
token_usage_tracker = {
    'requests': [],  # Liste von (timestamp, tokens) Tupeln
    'total_tokens_last_minute': 0
}


def generate(prompt, data):
    print("AI Batch generating...")
    settings = config('LLM')

    check_rate_limit()

    # Claude Client initialisieren
    client = anthropic.Anthropic(
        api_key=os.getenv('CLAUDE_KEY')
    )

    # Message History aufbauen
    messages = []
    if data is not None and data.get('history') is not None:
        # Bestehende History aus data übernehmen
        messages = data['history']

    # JSON-spezifische Prompt-Anpassung
    json_instruction = """

    IMPORTANT: Respond with valid JSON only. Your response must:
    1. Start with { and end with }
    2. Use proper JSON syntax with double quotes for strings
    3. Include no explanatory text outside the JSON structure
    4. Ensure all JSON is properly escaped

    Format your response as valid JSON."""

    final_prompt = prompt + json_instruction

    # Neue User Message hinzufügen
    messages.append({
        "role": "user",
        "content": final_prompt
    })

    # Batch-Request vorbereiten
    custom_id = f"req_{uuid.uuid4().hex[:8]}"

    api_params = {
        "model": settings['Model'],
        "messages": messages,
        "temperature": settings.get('Temperature', 0.7),
        "max_tokens": settings.get('Max_Output_Tokens', 4000),
    }

    # top_p nur hinzufügen wenn verfügbar
    if 'Top_p' in settings:
        api_params["top_p"] = settings['Top_p']

    batch_request = {
        "custom_id": custom_id,
        "params": api_params
    }

    # Batch mit einem Request erstellen
    print("📦 Batch wird erstellt...")
    try:
        message_batch = client.messages.batches.create(
            requests=[batch_request]
        )
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Batches: {e}")
        raise

    print(f"✅ Batch erstellt: {message_batch.id}")
    print(f"Status: {message_batch.processing_status}")

    # Auf Batch-Completion warten
    print("⏳ Warte auf Batch-Verarbeitung...")
    batch_result = wait_for_batch_completion(message_batch.id, client)

    if not batch_result:
        raise Exception("Batch-Verarbeitung fehlgeschlagen")

    # Erstes (und einziges) Ergebnis aus dem Batch holen
    result_entry = batch_result[0]

    # Error-Handling für verschiedene Result-Types
    if result_entry['result_type'] == 'errored':
        raise Exception(f"API-Fehler")
    elif result_entry['result_type'] == 'expired':
        raise Exception("Request ist abgelaufen")
    elif result_entry['result_type'] != 'succeeded':
        raise Exception(f"Unbekannter Result-Type: {result_entry['result_type']}")

    # Message-Objekt aus dem Erfolgs-Result extrahieren
    message_result = result_entry['message']

    # Token-Nutzung verarbeiten
    usage_metadata = message_result.usage
    used_tokens = 0
    if data is not None and data.get('used_tokens') is not None:
        used_tokens = data['used_tokens']

    # Claude gibt input_tokens und output_tokens zurück
    total_tokens_this_request = usage_metadata.input_tokens + usage_metadata.output_tokens
    used_tokens += total_tokens_this_request

    # Token-Nutzung zu Tracker hinzufügen (für Rate-Limiting)
    current_time = datetime.now()
    token_usage_tracker['requests'].append((current_time, usage_metadata.output_tokens))

    if usage_metadata:
        print(f"\n--- Token-Nutzung ---")
        print(f"Prompt Tokens dieser Anfrage: {usage_metadata.input_tokens}")
        print(f"Antwort Tokens dieser Anfrage: {usage_metadata.output_tokens}")
        print(f"Gesamt Tokens dieser Anfrage: {total_tokens_this_request}")
        print(f"Gesamt Tokens über alle Anfragen: {used_tokens}")

    # Text der Antwort extrahieren
    response_text = message_result.content[0].text

    # Antwort zur Historie hinzufügen
    messages.append({
        "role": "assistant",
        "content": response_text
    })

    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*$', '', response_text)

    print("AI Batch generated.")
    return {
        "response": response_text,
        "used_tokens": used_tokens
    }


def wait_for_batch_completion(batch_id, client, check_interval=30):
    """Wartet bis Batch fertig ist und gibt Ergebnisse zurück"""

    while True:
        batch = client.messages.batches.retrieve(batch_id)

        if batch.processing_status == "ended":
            print("✅ Batch-Verarbeitung abgeschlossen!")
            return get_batch_results(batch_id, client)
        elif batch.processing_status == "failed":
            print("❌ Batch fehlgeschlagen!")
            return None
        elif batch.processing_status == "canceled":
            print("⚠️ Batch wurde abgebrochen!")
            return None
        else:
            print(f"⏳ Batch Status: {batch.processing_status} (nächste Prüfung in {check_interval}s)")
            time.sleep(check_interval)


def get_batch_results(batch_id, client):
    """Holt die Ergebnisse eines fertigen Batches"""
    batch = client.messages.batches.retrieve(batch_id)

    if batch.processing_status != "ended":
        print(f"Batch noch nicht fertig. Status: {batch.processing_status}")
        return None

    # Results über Client-Methode laden (nicht direkt über URL!)
    results = []
    try:
        for result in client.messages.batches.results(batch_id):
            # Error-Handling je nach Result-Type
            match result.result.type:
                case "succeeded":
                    print(f"✅ Success: {result.custom_id}")
                    # Als Dictionary speichern für konsistente Verarbeitung
                    results.append({
                        "custom_id": result.custom_id,
                        "result_type": result.result.type,
                        "message": result.result.message,
                        "usage": result.result.message.usage
                    })
                case "errored":
                    if result.result.error.type == "invalid_request":
                        print(f"❌ Validation error {result.custom_id}: {result.result.error}")
                    else:
                        print(f"❌ Server error {result.custom_id}: {result.result.error}")
                    # Für Error-Cases
                    results.append({
                        "custom_id": result.custom_id,
                        "result_type": result.result.type,
                        "error": result.result.error
                    })
                case "expired":
                    print(f"⏰ Request expired: {result.custom_id}")
                    results.append({
                        "custom_id": result.custom_id,
                        "result_type": result.result.type
                    })

        print(f"📄 {len(results)} Batch-Ergebnisse verarbeitet")
        return results

    except Exception as e:
        print(f"❌ Fehler beim Laden der Batch-Ergebnisse: {e}")
        return None


def check_rate_limit():
    """
    Prüft das Rate-Limit und wartet wenn nötig
    Für Batch API weniger relevant, aber beibehalten für Konsistenz
    """
    settings = config('LLM')

    # Konfigurierbare Limits (falls nicht in config, verwende Standard-Werte)
    max_tokens_per_minute = settings.get('Max_Tokens_Per_Minute', 8000)  # https://docs.anthropic.com/en/api/rate-limits
    safety_buffer = settings.get('Rate_Limit_Buffer', 0.8)  # 80% des Limits nutzen

    effective_limit = int(max_tokens_per_minute * safety_buffer)

    current_time = datetime.now()
    one_minute_ago = current_time - timedelta(minutes=1)

    # Entferne alte Einträge (älter als 1 Minute)
    token_usage_tracker['requests'] = [
        (timestamp, tokens) for timestamp, tokens in token_usage_tracker['requests']
        if timestamp > one_minute_ago
    ]

    # Berechne Tokens in der letzten Minute
    tokens_last_minute = sum(tokens for _, tokens in token_usage_tracker['requests'])
    token_usage_tracker['total_tokens_last_minute'] = tokens_last_minute

    print(
        f"Rate-Limit Check: {tokens_last_minute}/{effective_limit} ({safety_buffer * 100}% des Limits) Tokens in letzter Minute")

    # Wenn wir nahe am Limit sind, warte
    if tokens_last_minute >= effective_limit:
        # Finde den ältesten Request in der letzten Minute
        if token_usage_tracker['requests']:
            oldest_request_time = min(timestamp for timestamp, _ in token_usage_tracker['requests'])
            wait_until = oldest_request_time + timedelta(minutes=1)
            wait_seconds = (wait_until - current_time).total_seconds()

            if wait_seconds > 0:
                print(f"⏳ Rate-Limit erreicht! Warte {wait_seconds:.1f} Sekunden...")
                time.sleep(wait_seconds + 1)  # +1 Sekunde Puffer
                print("✅ Rate-Limit-Wartezeit beendet, setze fort...")