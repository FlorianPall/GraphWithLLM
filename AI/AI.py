import json
from Helper.Files import config, get_prompt, csv_semicolon
from AI.AIConnector import generate

def simplify_competences(competences, log_callback, data=None):
    simplify_prompt = get_prompt("Simplify", log_callback)
    return generate(simplify_prompt + json.dumps(competences), data, log_callback)


def translate_modules(modules, log_callback, data=None):
    translate_prompt = get_prompt("Translate", log_callback)
    return generate(translate_prompt + json.dumps(modules), data, log_callback)


def connected_esco(skills, log_callback, data=None):
    esco_prompt = get_prompt("ConnectESCO", log_callback)
    esco_skills_filename = config('Caching', log_callback)['ESCO_preferred_label']
    esco_skills = csv_semicolon("./src/Output/" + esco_skills_filename)
    esco_skills_str = esco_skills.to_csv(sep=';', index=False)
    return generate(esco_prompt + json.dumps(
        skills) + "\n Do not use other esco skills like these under any circumstances. This are the labels: \n" + esco_skills_str,
                    data, log_callback)


def create_cipher(graph, log_callback, data=None):
    cipher_prompt = get_prompt("Graph", log_callback)
    return generate(cipher_prompt + json.dumps(graph), data, log_callback)


def matrix(graph, log_callback, data=None):
    matrix_prompt = get_prompt("Matrix", log_callback)
    return generate(matrix_prompt + json.dumps(graph), data, log_callback)


def graph_json(graph, log_callback, data=None):
    graph_prompt = get_prompt("Graph_JSON", log_callback)
    node_structure = config('LLM_Structure', log_callback)
    return generate(graph_prompt + graph + '\n YAML Structure: \n' + str(node_structure), data, log_callback)

def cluster_nodes(nodes, log_callback, data=None):
    cluster_prompt = get_prompt("AINodeClustering", log_callback) + json.dumps(nodes)
    return generate(cluster_prompt, data, log_callback)