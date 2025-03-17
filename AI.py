import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from Files import config, get_prompt

load_dotenv("./DB/.env")

def simplify_competences(competences, data = None):
    simplify_prompt = get_prompt("Simplify")
    return generate(simplify_prompt + json.dumps(competences), data)

def translate_modules(modules, data = None):
    translate_prompt = get_prompt("Translate")
    return generate(translate_prompt + json.dumps(modules), data)

def connected_esco(skills, data = None):
    esco_prompt = get_prompt("ConnectESCO")
    return generate(esco_prompt + json.dumps(skills), data)

def create_cipher(graph, data = None):
    cipher_prompt = get_prompt("Graph")
    return generate(cipher_prompt + json.dumps(graph), data)

def matrix(graph, data = None):
    matrix_prompt = get_prompt("Matrix")
    return generate(matrix_prompt + json.dumps(graph), data)

def graph_json(graph, data = None):
    graph_prompt = get_prompt("Graph")
    return generate(graph_prompt + graph, data)

def generate(prompt, data):
    print("AI generating...")
    settings = config('LLM')
    client = genai.Client(
        api_key=os.getenv('API_KEY'),
    )
    history = []
    if data is not None and data['history'] is not None:
        history = data['history']
    model = settings['Model']
    history.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    )
    generate_content_config = types.GenerateContentConfig(
        temperature=settings['Temperature'],
        top_p=settings['Top_p'],
        top_k=settings['Top_k'],
        max_output_tokens=settings['Max_Output_Tokens'],
        response_mime_type=settings['Response_Mime_Type'],
    )

    # Für Token-Zählung benötigen wir die vollständige Antwort
    response_obj = client.models.generate_content(
        model=model,
        contents=history,
        config=generate_content_config,
    )

    # Token-Nutzung ausgeben
    usage_metadata = response_obj.usage_metadata
    used_tokens = 0
    if data is not None and data['used_tokens'] is not None:
        used_tokens = data['used_tokens']
    used_tokens += usage_metadata.total_token_count
    if usage_metadata:
        print(f"\n--- Token-Nutzung ---")
        print(f"Prompt Tokens dieser Anfrage: {usage_metadata.prompt_token_count}")
        print(f"Antwort Tokens dieser Anfrage: {usage_metadata.candidates_token_count}")
        print(f"Gesamt Tokens dieser Anfrage: {usage_metadata.total_token_count}")
        print(f"Gesamt Tokens über alle Anfragen: {used_tokens}")

    # Text der Antwort extrahieren
    response = response_obj.text

    # Antwort zur Historie hinzufügen
    history.append(
        types.Content(
            role="model",
            parts=[types.Part.from_text(text=response)],
        )
    )
    print("AI generated.")
    return {
        "response": response,
        "used_tokens": used_tokens,
        "history": history
    }