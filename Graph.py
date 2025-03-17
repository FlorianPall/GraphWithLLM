from AI import create_cipher, matrix, graph_json
from Files import cache, write_txt_cache, config, write_json_cache
import json

def create_cipher():
    filename = config('Caching')['Merged_Graph_ESCO_JSON']
    graph = cache(filename)
    data = create_cipher(graph)
    cipher_graph = json.loads(data['response'])
    filename = config('Caching')['LLM_Graph']
    write_txt_cache(cipher_graph, filename)
    return data

def create_json_graph():
    filename = config('Caching')['PDF_JSON']
    graph = cache(filename)
    data = matrix(graph)
    matrix_response = data['response']

    data = graph_json(matrix_response, data)
    generated_graph_json = json.loads(data['response'])
    filename = config('Caching')['LLM_Graph']
    write_json_cache(generated_graph_json, filename)
    return data