import json

from Helper.Files import cache, config, write_json_cache
from AI.AI import cluster_nodes
def merge(cache_folder, log_callback, set_process_complete, set_process_error):
    data = cache(config('Caching', log_callback)['Graph_JSON'], cache_folder, log_callback)
    ignored_properties = config('Ignored_Properties_Merging', log_callback)
    ignored_nodes = config('Ignored_Nodes_Merging', log_callback)
    node_map = extract(data, ignored_properties, ignored_nodes)
    duplicates = detect_duplicates(node_map)
    connections_of_duplicates(duplicates, data)
    write_json_cache(data, cache_folder, config('Caching', log_callback)['Merged_Graph_JSON'], log_callback)
    ai_merge_nodes(data, cache_folder, log_callback)
    set_process_complete()

def extract(data, ignored_properties, ignored_nodes):
    node_map = {}
    for node in data['nodes']:
        if node['label'] in ignored_nodes:
            continue
        filtered_props = {k: v for k, v in node['properties'].items() if k not in ignored_properties}
        hash_data = (node['label'], tuple(sorted(filtered_props.items())))
        name = hash(str(hash_data))
        if name not in node_map:
            node_map[name] = []
            node_map[name].append(node)
        else:
            node_map[name].append(node)
    return node_map

def detect_duplicates(node_map):
    duplicates = {}
    for node_name, nodes in node_map.items():
        if len(nodes) > 1:
            duplicates[node_name] = {
                'count': len(nodes),
                'ids': [node['id'] for node in nodes]
            }
    return duplicates

def connections_of_duplicates(duplicates, data):
    for node_name, duplicate in duplicates.items():
        correct_id = duplicate['ids'][0]
        for node_id in duplicate['ids'][1:]:
            relationship(node_id, correct_id, data)
            data['nodes'] = [node for node in data['nodes'] if node['id'] != node_id]

def relationship(node_id, correct_id, data):
    relations = data['relationships']
    for node in relations:
        if node['startNode'] == node_id:
            change_relationship_start_node(node_id, node['endNode'], correct_id, data)
        if node['endNode'] == node_id:
            change_relationship_end_node(node['startNode'], node_id, correct_id, data)

def change_relationship_start_node(old_start, end, new_start, data):
    for relation in data["relationships"]:
        if relation["startNode"] == old_start and relation["endNode"] == end:
            relation["startNode"] = new_start
            break

def change_relationship_end_node(start, old_end, new_end, data):
    for relation in data["relationships"]:
        if relation["startNode"] == start and relation["endNode"] == old_end:
            relation["endNode"] = new_end
            break

def ai_merge_nodes(data, cache_folder, log_callback):
    nodes = data['nodes']
    skills = list(filter(lambda node: node['label'] == 'Skill', nodes))
    result = cluster_nodes(skills)
    response = json.loads(result['response'])
    response = list(filter(lambda group: len(group['ids']) > 1, response))
    write_json_cache(response, cache_folder, config('Caching', log_callback)['AI_Clustered_Graph_JSON'], log_callback)

    # print Statement und Bestätigung
    log_callback(
        "\n\n\nACHTUNG: Prüfe die Cluster Datei und Bestätige mit Enter. Es ist möglich Modifikationen vorzunehmen. ACHTUNG: Die Daten in originalNodes dienen nur der Dokumentation und werden nicht mehr beachtet werden.")
    #input()  # Warten auf Enter

    # Datei neu einlesen
    clustered_data = cache(config('Caching', log_callback)['AI_Clustered_Graph_JSON'], cache_folder, log_callback)

    # Clustering auf data anwenden
    apply_clustering_to_data(data, clustered_data)
    write_json_cache(data, cache_folder, config('Caching', log_callback)['AI_Clustered_Graph_JSON'], log_callback)
    return data


def apply_clustering_to_data(data, clustered_data):
    """
    Wendet das Clustering auf die ursprünglichen Daten an
    """
    # Sammle alle IDs die gruppiert werden sollen
    grouped_skill_ids = set()
    id_mapping = {}  # Mapping von alter ID zu neuer ID

    for group in clustered_data:
        grouped_skill_ids.update(group['ids'])

    # Finde die höchste bestehende ID für neue IDs
    max_id = max(node['id'] for node in data['nodes'])
    next_id = max_id + 1

    # Füge neue gruppierte Nodes hinzu und erstelle ID-Mapping
    for group in clustered_data:
        new_node = {
            "id": next_id,
            "label": group['label'],
            "properties": group['properties']
        }
        data['nodes'].append(new_node)

        # Erstelle Mapping für alle IDs in der Gruppe
        for old_id in group['ids']:
            id_mapping[old_id] = next_id

        next_id += 1

    # Update alle Relationships mit dem ID-Mapping
    update_all_relationships(data, id_mapping)

    # Entferne die ursprünglichen gruppierten Skills
    data['nodes'] = [node for node in data['nodes']
                     if not (node['label'] == 'Skill' and node['id'] in grouped_skill_ids)]

def update_all_relationships(data, id_mapping):
    """
    Aktualisiert alle Relationships basierend auf dem ID-Mapping
    """
    updated_count = 0

    for current_relationship in data['relationships']:
        # Update startNode wenn es in der Mapping ist
        start_node_id = int(current_relationship['startNode'])
        if start_node_id in id_mapping:
            current_relationship['startNode'] = str(id_mapping[start_node_id])
            updated_count += 1

        # Update endNode wenn es in der Mapping ist
        end_node_id = int(current_relationship['endNode'])
        if end_node_id in id_mapping:
            current_relationship['endNode'] = str(id_mapping[end_node_id])
            updated_count += 1

    # Entferne doppelte Relationships
    remove_duplicate_relationships_simple(data)
    remove_useless_relationships(data)

def remove_duplicate_relationships_simple(data):
    """
    Entfernt doppelte Relationships die durch das Clustering entstanden sein könnten
    """
    seen_relationships = set()
    unique_relationships = []

    for rel in data['relationships']:
        # Erstelle einen eindeutigen Key für die Relationship
        rel_key = (rel['startNode'], rel['endNode'], rel['type'])

        if rel_key not in seen_relationships:
            seen_relationships.add(rel_key)
            unique_relationships.append(rel)

    data['relationships'] = unique_relationships


def remove_useless_relationships(data):
    """
    Entfernt Relationships, die den gleichen Start- und Endknoten haben
    """
    relationships = data['relationships']
    useless_relationships = [
        rel for rel in relationships if rel['startNode'] == rel['endNode']
    ]
    if useless_relationships:
        data['relationships'] = [
            rel for rel in relationships if rel not in useless_relationships
        ]