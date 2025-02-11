from pdfminer.high_level import extract_pages
import yaml
import json

STRUCTURE_PATH = "./src/Modules/structure.yml"


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
    try:
        keywords = []
        with open(STRUCTURE_PATH, 'r') as f:
            file = yaml.safe_load(f)
            for category, titles in file.items():
                for title in titles:
                    keywords.append((word_to_lower_and_without_spaces(category), word_to_lower_and_without_spaces(title)))

        return keywords
    except yaml.YAMLError as e:
        print(f"YAML Fehler: {e}")
    except FileNotFoundError:
        print("Datei nicht gefunden")

def groups_by_structure(pdf_data, pdf_structure):
    result = {}
    current_key = None
    current_category = None
    current_content = []
    counter = 1

    # Erstelle Dict für schnelleren Lookup: {searchterm: category}
    structure_dict = {searchterm: category
                      for category, searchterm in pdf_structure}

    for group in pdf_data[1:]:  # Überspringe die erste Gruppe (Header)
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

    # Füge letzten Inhalt hinzu
    if current_category:
        result[current_category] = current_content

    return {
        key: value
        for key, value in result.items()
        if "literature" not in key
    }

def extract_pdf():
    try:
        pages = list(extract_pages("./src/Modules/2_Module.pdf"))
        pdf_data = pdf_groups(pages)
        pdf_structure = load_pdf_structure()
        structured_data = groups_by_structure(pdf_data, pdf_structure)
        print(json.dumps(structured_data, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Fehler beim Verarbeiten der PDF: {str(e)}")