from AI.AI import create_cipher, matrix, graph_json
from Helper.Files import cache, write_txt_cache, config, write_json_cache
import json


def create_cipher_graph(data, cache_folder, log_callback, set_process_complete, set_process_error):
    filename = config('Caching', log_callback)['Merged_Graph_ESCO_JSON']
    graph = cache(filename, cache_folder, log_callback)
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
    filename = config('Caching', log_callback)['LLM_Graph']
    write_txt_cache(cypher_query, cache_folder, filename, log_callback)
    set_process_complete(data)

def create_json_graph(data, cache_folder, log_callback, set_process_complete, set_process_error):
    filename = config('Caching', log_callback)['Pdf_JSON']
    graph = cache(filename, cache_folder, log_callback)
    data = matrix(graph, data)
    matrix_response = data['response']

    data = graph_json(matrix_response, data)
    generated_graph_json = json.loads(data['response'])
    filename = config('Caching', log_callback)['Graph_JSON']
    write_json_cache(generated_graph_json, cache_folder, filename, log_callback)
    return set_process_complete(data)