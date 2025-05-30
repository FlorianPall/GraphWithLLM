from Files import config, cache, write_json_cache
from AI import connected_esco
import json
from DBEngine import get_engine
from sqlalchemy import text
# PostgreSQL Verbindung erstellen
engine = get_engine()

def read_data():
    filename = config('Caching')['Merged_Graph_JSON']
    data = cache(filename)
    return data

def extract_skills(data):
    skills = {}
    for node in data['nodes']:
        if node['label'] == 'Skill':
            skills[node['id']] = {"Skill": node['properties']['name'], "Description": node['properties']['description']}
    return skills

def connected_esco_skills(skills, data):
    return connected_esco(skills, data)

def esco_skills(extracted_skills):
    preferred_labels = [pair[1] for pair in extracted_skills]
    esco = {}
    with engine.connect() as connection:
        for label in preferred_labels:
            query = text("""
                         SELECT concepturi, preferredLabel, altlabels, description
                         FROM skills
                         WHERE preferredlabel ILIKE :label LIMIT 1;
                         """)

            result = connection.execute(query, {"label": label})

            row = result.fetchone()
            if row:
                row_dict = {column: value for column, value in zip(result.keys(), row)}
                esco[label] = row_dict
            else:
                esco[label] = None
    return esco

def add_esco_to_graph(skills, data, connected_skills):
    # Add Nodes
    counter = 1
    for skill in skills:
        current_skill = skills[skill]
        if current_skill is None:
            print("ERROR: No ESCO Skill found for: " + str(skill))
            connected_skills = [connection for connection in connected_skills if connection[1] != skill]
            continue

        data['nodes'].append({
            "id": 'E' + str(counter),
            "label": "ESCO",
            "properties": {
                "name": skills[skill].get('preferredlabel', "ERROR"),
                "description": skills[skill]['description'],
                "altlabels": skills[skill]['altlabels'],
                "concepturi": skills[skill]['concepturi']
            }
        })

        for i, connection in enumerate(connected_skills):
            if connection[1] == skill:
                connected_skills[i][1] = 'E' + str(counter)
        counter += 1
# Add relationships
    for connection in connected_skills:
        data['relationships'].append({
            "startNode": connection[0],
            "endNode": connection[1],
            "type": connection[2],
            "properties": {}
        })


def connect_esco(data):
    json_graph = read_data()
    extracted_skills = extract_skills(json_graph)
    data = connected_esco_skills(extracted_skills, data)
    connected_skills = json.loads(data['response'])
    skills = esco_skills(connected_skills)
    add_esco_to_graph(skills, json_graph, connected_skills)
    write_json_cache(json_graph, config('Caching')['Merged_Graph_ESCO_JSON'])
    return data