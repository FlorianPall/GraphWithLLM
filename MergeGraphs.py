from ReadFiles import cache
from ReadFiles import config
import json

def merge():
    data = cache('Graph_JSON.json')
    ignored_properties = config('Ignored_Properties_Merging')
    ignored_nodes = config('Ignored_Nodes_Merging')
    node_map = extract(data, ignored_properties, ignored_nodes)
    duplicates = detect_duplicates(node_map)
    connections_of_duplicates(duplicates, data)
    write_json_cache(data)

def properties_equal(prop1, prop2, ignored_properties):
    prop1_filtered = {k: v for k, v in prop1.items() if k not in ignored_properties}
    prop2_filtered = {k: v for k, v in prop2.items() if k not in ignored_properties}
    return prop1_filtered == prop2_filtered

def extract(data, ignored_properties, ignored_nodes):
    node_map = {}
    for node in data['nodes']:
        if node['label'] in ignored_nodes:
            continue
        name = hash(str(sorted(node['properties'].items())))
        if name not in node_map:
            node_map[name] = []
            node_map[name].append(node)
        else:
            for current_node in node_map[name]:
                if properties_equal(current_node['properties'], node['properties'], ignored_properties) and current_node['label'] == node['label']:
                    node_map[name].append(node)
                    break
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

def write_json_cache(data):
    try:
        filename = config('Caching')['Merged_Graph_JSON']
        print("Writing to file: " + filename)
        with open('./src/Cache/' + filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing to file: {e}")