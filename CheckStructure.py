import yaml
import re

def check_structure (path, config_name, graph_name):
    print("Start Checking the structure of the input file")
    graph = load_graph(path, graph_name)
    relationships = extract_graph_connections(graph)
    config = load_graph_config(path, config_name)
    lines = check_graph_structure(relationships, config)
    print("Lines with errors (Anzahl: " + str(len(lines)) + "):" + str(lines))
    if len(lines) > 0:
        graph_splits = delete_lines_in_graph(graph, lines)
        check_with_statements(graph_splits)
        file_ending(graph_splits)
    else:
        graph_splits = split_graph(graph)
    write_graph(path, graph_splits, graph_name)

def load_graph_config (path, config_name):
    print("Start loading the graph configuration")
    path = path + "/" + config_name
    # Mit Fehlerbehandlung
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"YAML Fehler: {e}")
    except FileNotFoundError:
        print("Datei nicht gefunden")

def load_graph (path, graph_name):
    print("Start loading the graph")
    path = path + "/" + graph_name
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Datei nicht gefunden")
    except UnicodeDecodeError:
        print("Fehler beim Dekodieren")

def split_graph (graph):
    print("Start splitting the graph")
    return graph.split("\n")

def extract_graph_connections (graph):
    print("Start checking the graph connections")
    graph_splits = split_graph(graph)
    relationships = []
    for line_num, line in enumerate(graph_splits, 1):
        matches = re.finditer(r'\(([\w:]+)\)-\[:(\w+)\]->\(([\w:]+)\)', line)

        for match in matches:
            from_node = match.group(1)
            to_node = match.group(3)
            relationships.append({
                'from': get_node_name(from_node, graph),
                'to': get_node_name(to_node, graph),
                'line': line_num
            })

    return relationships

def get_node_name (node, graph):
    match = re.search(rf'{node}:(\w+)', graph)
    if match:
        return match.group(1)
    else:
        print(f"Node {node} not found in graph")
        return None

def check_graph_structure (relationships, config):
    print("Start Checking the structure of the input file")
    relationships_with_errors = []
    node_map = {}
    for node in config['Nodes']:
        node_map[node['Name']] = {edge['Target']: edge['Properties'] for edge in node.get('Edges', [])}

    for relationship in relationships:
        from_node = relationship['from']
        to_node = relationship['to']
        if not check_node_map(from_node, to_node, node_map):
            relationships_with_errors.append(relationship)
    return relationships_with_errors

def check_node_map(from_node, to_node, node_map):
    from_node_found = False
    to_node_found = False
    connection_found = False

    for node in node_map:
        if from_node in node and not from_node_found:
            from_node_found = True
            from_node = node
        if to_node in node and not to_node_found:
            to_node_found = True
            to_node = node
        if from_node_found and to_node_found:
            break
    if from_node_found and to_node_found and to_node in node_map[from_node]:
        connection_found = True
    return from_node_found and to_node_found and connection_found

def delete_lines_in_graph (graph, lines):
    print("Start deleting lines in the graph")
    graph_splits = split_graph(graph)
    lines = sorted(lines, key=lambda x: x['line'], reverse=True)
    for line in lines:
        graph_splits.pop(line['line'] - 1)
    return graph_splits

def check_with_statements (graph_splits):
    print("Start checking the graph with statements")
    with_statements = []
    for line_num, line in enumerate(graph_splits, 1):
        if line.startswith("WITH "):
            with_statements.append(line_num)
    for with_statement in with_statements:
        counter = 2
        while True:
            if len(graph_splits[with_statement - counter]) > 0 and not graph_splits[with_statement - counter].startswith("//"):
                if graph_splits[with_statement - counter].endswith(","):
                    graph_splits[with_statement - counter] = graph_splits[with_statement - counter][:-1]
                break
            counter += 1

def file_ending (graph_splits):
    print("Start checking the file ending")
    while True:
        if not graph_splits[-1].endswith(";"):
            if graph_splits[-1].startswith("//") or graph_splits[-1].startswith("WITH ") or len(graph_splits[-1]) == 0:
                graph_splits.pop(-1)
            elif graph_splits[-1].endswith(","):
                graph_splits[-1] = graph_splits[-1][:-1]
            else:
                graph_splits[-1] = graph_splits[-1] + ";"
                break

def write_graph(path, lines, graph_name):
    print("Start writing the graph")
    path = path + "/" + graph_name.split(".")[0] + "_Output.txt"
    try:
        with open(path, 'w') as f:
            f.write("\n".join(lines))
    except FileNotFoundError:
        print("Datei nicht gefunden")
    except UnicodeDecodeError:
        print("Fehler beim Dekodieren")

