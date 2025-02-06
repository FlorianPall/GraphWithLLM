from pdfminer.high_level import extract_pages
import os


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


def extract_pdf():
    try:
        pages = list(extract_pages("./src/Modules/SE_I_German.pdf"))
        for page_num, page in enumerate(pages, 1):
            print(f"\nSeite {page_num}:")

            # Sammle alle TextBoxes von der Seite
            text_boxes = [element for element in page if hasattr(element, 'get_text')]

            # Gruppiere die Textboxen
            grouped_boxes = group_text_boxes(text_boxes)

            # Gib die Gruppen aus
            for i, group in enumerate(grouped_boxes, 1):
                print(f"\nGruppe {i}:")
                for box in group:
                    print(f"{box.get_text().strip()}")
                print("-" * 50)

    except Exception as e:
        print(f"Fehler beim Verarbeiten der PDF: {str(e)}")