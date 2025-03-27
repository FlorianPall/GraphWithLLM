from Files import config, write_json_cache
from AI import simplify_competences, translate_modules
from pdfminer.high_level import extract_pages
import json


def group_text_boxes(text_boxes):
    # Sortiere nach y-Position (von oben nach unten)
    sorted_boxes = sorted(text_boxes, key=lambda box: -float(box.bbox[1]))

    groups = []
    current_group = []
    last_right_edge = 0

    for box in sorted_boxes:
        left_edge = float(box.bbox[0])

        # Wenn die linke Kante links von der vorherigen rechten Kante liegt
        if left_edge < last_right_edge:
            # Speichere aktuelle Gruppe und starte neue
            if current_group:
                groups.append(current_group)
                current_group = []
            last_right_edge = 0

        current_group.append(box)
        # Aktualisiere die rechteste Kante
        last_right_edge = max(last_right_edge, float(box.bbox[2]))

    # Füge letzte Gruppe hinzu
    if current_group:
        groups.append(current_group)

    return groups

def word_to_lower_and_without_spaces(word):
    return word.lower().strip().replace(' ', '')

def pdf_groups(pages):
    try:
        all_groups = []

        for page in pages:
            # Sammle alle TextBoxes von der Seite
            text_boxes = [element for element in page if hasattr(element, 'get_text')]

            # Gruppiere die Textboxen
            grouped_boxes = group_text_boxes(text_boxes)

            # Extrahiere nur die Texte aus jeder Gruppe
            for group in grouped_boxes:
                group_texts = [box.get_text().strip() for box in group]
                all_groups.append(group_texts)

        return all_groups

    except Exception as e:
        return f"Fehler beim Verarbeiten der PDF: {str(e)}"

def load_pdf_structure():
    keywords = []
    for category, titles in config('Modulestructure').items():
        for title in titles:
            keywords.append((word_to_lower_and_without_spaces(category), word_to_lower_and_without_spaces(title)))

    return keywords

def groups_by_structure(pdf_data, pdf_structure):
    result = {}
    current_category = None
    current_content = []
    counter = 1

    # Erstelle Dict für schnelleren Lookup: {searchterm: category}
    structure_dict = {searchterm: category
                      for category, searchterm in pdf_structure}

    for group in pdf_data:  # Überspringe die erste Gruppe (Header)
        text = group[0] if group else ""
        text_normalized = word_to_lower_and_without_spaces(text)

        # Prüfe ob aktuelle Gruppe einem Searchterm entspricht
        if text_normalized in structure_dict:
            # Speichere vorherigen Inhalt wenn vorhanden
            if current_category:
                result[current_category] = current_content
                counter += 1
            # Starte neue Sektion mit der Kategorie als Key
            current_category = structure_dict[text_normalized] + str(counter)
            current_content = []
        else:
            # Füge Inhalt zur aktuellen Sektion hinzu
            if current_category:  # Nur hinzufügen wenn wir eine aktuelle Kategorie haben
                current_content.append(group)
            else:
                result["header" + str(counter)] = group
                counter += 1

    # Füge letzten Inhalt hinzu
    if current_category:
        result[current_category] = current_content

    return process_pdf_data(result)

def process_pdf_data(data):
    output = {}

    for key, value in data.items():
        # Prüfen ob es sich um einen literature-Key handelt
        if "literature" in key:
            # Prüfen ob mehr als 2 Arrays vorhanden sind
            if isinstance(value, list) and len(value) > 2:
                # Neuen Header-Key erstellen (gleiche Nummer wie literature)
                header_key = f"header{key.replace('literature', '')}"
                # Nur das letzte Array übernehmen
                values = value[-1]
                output[header_key] = []
                for val in values:
                    output[header_key].append(val)
                continue

        # Wenn der Suchstring nicht im Key ist, Key-Value-Paar übernehmen
        else:
            output[key] = value

    return output

def structure_to_correct_form(structure):
    if not structure:
        return {}

    result = {}
    current_header = None

    def process_values(values, is_paired=False):
        """Verarbeitet die Werte je nach Format (gepaart oder einzeln)"""
        if not is_paired:
            if len(values) == 1:
                return values
            if len(values[0]) == len(values[1]):
                pair = process_values([values[0], values[1]], True)
                return_value = pair
                for i in range(2, len(values)):
                    return_value.append(values[i])
                return return_value

        paired_results = []
        for i in range(0, len(values), 2):
            if i + 1 >= len(values):
                break
            keys, vals = values[i], values[i + 1]
            paired_results.extend(
                {key: val} for key, val in zip(keys, vals)
            )
        return paired_results

    def remove_numbers(text):
        """Entfernt Zahlen aus einem String"""
        return ''.join(char for char in text if not char.isdigit())

    for key, value in structure.items():
        if not value:  # Überprüfe auf leere Werte
            continue

        if 'header' in key.lower():
            try:
                current_header = value[-1]
                result[current_header] = []
            except IndexError:
                continue

        else:
            if not current_header:
                continue

            local_key = remove_numbers(key)
            current_entry = {local_key: []}
            result[current_header].append(current_entry)

            # Bestimme, ob die Werte gepaart sind (gerade Anzahl)
            is_paired = len(value) % 2 == 0
            processed_values = process_values(value, is_paired)

            current_entry[local_key].extend(processed_values)

    return result

def extract_competences(data):
    structure = {}
    for key, values in data.items():
        parts = key.split('\n', 1)
        for value in values:
            if 'competences' in value:
                structure[parts[0]] = value
    return structure

def replace_competences(data, competences):
    for module_key in data.keys():
        matching_key = None
        for new_key in competences.keys():
            if new_key in module_key:
                matching_key = new_key
                break

        if matching_key:
            for i, section in enumerate(data[module_key]):
                if "competences" in section:
                    data[module_key][i] = {"competences": competences[matching_key]["competences"]}

def extract_pdf(filename, data):
    try:
        pages = list(extract_pages("./src/Modules/" + filename))
        pdf_data = pdf_groups(pages)
        pdf_structure = load_pdf_structure()
        structured_data = groups_by_structure(pdf_data, pdf_structure)
        correct_form = structure_to_correct_form(structured_data)
        data = translate_modules(correct_form, data)
        correct_form = json.loads(data['response'])
        competences = extract_competences(correct_form)
        data = simplify_competences(competences, data)
        replace_competences(correct_form, json.loads(data['response']))
        write_json_cache(correct_form, config('Caching')['Pdf_JSON'])
        return data
    except Exception as e:
        print(f"Fehler beim Verarbeiten der PDF: {str(e)}")
        return None
