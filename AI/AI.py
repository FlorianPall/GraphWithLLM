import json
from Helper.Files import config, get_prompt, csv_semicolon
from AI.AIConnector import generate

def simplify_competences(competences, data=None):
    simplify_prompt = get_prompt("Simplify")
    return generate(simplify_prompt + json.dumps(competences), data)


def translate_modules(modules, data=None):
    translate_prompt = get_prompt("Translate")
    return generate(translate_prompt + json.dumps(modules), data)


def connected_esco(skills, data=None):
    esco_prompt = get_prompt("ConnectESCO")
    esco_skills_filename = config('Caching')['ESCO_preferred_label']
    esco_skills = csv_semicolon("./src/Output/" + esco_skills_filename)
    esco_skills_str = esco_skills.to_csv(sep=';', index=False)
    return generate(esco_prompt + json.dumps(
        skills) + "\n Do not use other esco skills like these under any circumstances. This are the labels: \n" + esco_skills_str,
                    data)


def create_cipher(graph, data=None):
    cipher_prompt = get_prompt("Graph")
    return generate(cipher_prompt + json.dumps(graph), data)


def matrix(graph, data=None):
    matrix_prompt = get_prompt("Matrix")
    return generate(matrix_prompt + json.dumps(graph), data)


def graph_json(graph, data=None):
    graph_prompt = get_prompt("Graph_JSON")
    node_structure = config('LLM_Structure')
    return generate(graph_prompt + graph + '\n YAML Structure: \n' + str(node_structure), data)

def cluster_nodes(nodes, data=None):
    cluster_prompt = get_prompt("AINodeClustering") + json.dumps(nodes)
    return generate(cluster_prompt, data)