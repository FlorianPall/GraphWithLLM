from AI import create_cipher, matrix, graph_json
from Files import cache, write_txt_cache, config, write_json_cache
import json


def create_cipher_graph(data):
    filename = config('Caching')['Merged_Graph_ESCO_JSON']
    graph = cache(filename)
    data = create_cipher(graph, data)
    cipher_graph = json.loads(data['response'])
    if isinstance(cipher_graph, list):
        if len(cipher_graph) == 1 and isinstance(cipher_graph[0], dict) and 'query' in cipher_graph[0]:
            cipher_graph = cipher_graph[0]['query']
    elif isinstance(cipher_graph, dict) and 'query' in cipher_graph:
        cipher_graph = cipher_graph['query']

    cypher_query = ""

    if isinstance(cipher_graph, (list, tuple)) or (
            hasattr(cipher_graph, '__iter__') and not isinstance(cipher_graph, (str, dict))):
        for element in cipher_graph:
            cypher_query += str(element)
    elif isinstance(cipher_graph, str):
        cypher_query = cipher_graph
    else:
        cypher_query = str(cipher_graph)
    cypher_query += " RETURN 'Graph created successfully' as result"
    filename = config('Caching')['LLM_Graph']
    write_txt_cache(cypher_query, filename)
    return data

def create_json_graph(data):
    filename = config('Caching')['Pdf_JSON']
    graph = cache(filename)
    data = matrix(graph, data)
    matrix_response = data['response']

    data = graph_json(matrix_response, data)
    generated_graph_json = json.loads(data['response'])
    filename = config('Caching')['Graph_JSON']
    write_json_cache(generated_graph_json, filename)
    return data