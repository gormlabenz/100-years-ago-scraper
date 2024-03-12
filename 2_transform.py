import json
from datetime import datetime, timedelta
import os
import re


def convert_date_to_iso(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y (%A)")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return False


def extract_date_from_caption(caption):
    # Versucht, das Datum aus der Bildunterschrift zu extrahieren
    try:
        # Extrahiert den Teil vor dem ersten Doppelpunkt
        date_str = caption.split(":")[0]
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        return date_obj.strftime("%Y-%m-%d"), caption.split(": ", 1)[1]
    except ValueError:
        return False, caption


def transform_entries(entries):
    transformed = {}
    for entry in entries:
        iso_date, new_caption = extract_date_from_caption(entry['caption'])
        if iso_date:
            # Aktualisiert die Bildunterschrift ohne Datum
            entry['caption'] = new_caption
            if iso_date not in transformed:
                transformed[iso_date] = [entry]
            else:
                transformed[iso_date].append(entry)
    return transformed


def split_list_into_categories(entries):
    events = []
    births = []
    deaths = []
    category = 'events'  # Start with 'events' as the default category

    for entry in entries:
        text = entry.get('text', '')
        # Überprüft, ob es sich um einen Marker handelt, der nur die Kategorie ändert
        if text == "Born:":
            category = 'births'
            continue  # Überspringt das Hinzufügen des Kategorie-Wechselmarkers selbst
        elif text == "Died:":
            category = 'deaths'
            continue  # Überspringt das Hinzufügen des Kategorie-Wechselmarkers selbst

        # Wechselt die Kategorie, wenn der Eintrag mit "Born: " oder "Died: " beginnt
        if text.startswith('Born:'):
            category = 'births'
        elif text.startswith('Died:'):
            category = 'deaths'

        # Fügt den Eintrag der entsprechenden Kategorie hinzu
        if category == 'events':
            events.append(entry)
        elif category == 'births':
            # Entfernt das "Born: " aus dem Eintrag
            entry['text'] = entry['text'].replace(
                "**Born:**", "").replace("Born:", "").strip()
            births.append(entry)
        elif category == 'deaths':
            # Entfernt das "Died: " aus dem Eintrag
            entry['text'] = entry['text'].replace(
                "**Died:**", "").replace("Died:", "").strip()
            deaths.append(entry)

    return events, births, deaths


def get_images(section):
    images = []
    if "images" in section:
        for image in section["images"]:
            images.append(image)
    return images


def to_wikipedia_url(entry):
    base_url = "https://en.wikipedia.org/wiki/"
    if entry["type"] == "internal":
        page_name = entry["page"].replace(" ", "_")
        return base_url + page_name
    else:
        return entry.get("site", None)


def object_to_markdown(obj):
    text = obj["text"]
    formatting = obj.get("formatting", {})
    links = sorted(obj.get("links", []),
                   key=lambda x: len(x["page"]) if "page" in x else len(x["text"]), reverse=True)

    # Ersetze fett und kursiv
    if "bold" in formatting:
        for bold_text in formatting["bold"]:
            text = text.replace(bold_text, f"**{bold_text}**")
    if "italic" in formatting:
        for italic_text in formatting["italic"]:
            text = text.replace(italic_text, f"*{italic_text}*")

    # Ersetze Links
    for link in links:
        # Use "page" if "text" is not available
        if link["type"] == "internal":
            link_text = link.get("text", link["page"])
            link_url = to_wikipedia_url(link)
        else:  # Für externe Links
            link_text = link.get("text", link["site"])
            link_url = link["site"]

        # Suche nur Text, der noch nicht Teil eines Markdown-Links ist
        pattern = rf'(?<!\[)\b{re.escape(link_text)}\b(?!]\()'

        # Verwende nur den ersten Treffer, um Mehrfachersetzung zu vermeiden
        matches = list(re.finditer(pattern, text))
        if matches:
            # Ersetze den ersten Treffer durch Markdown-Link
            start, end = matches[0].span()
            text = text[:start] + f"[{link_text}]({link_url})" + text[end:]

    return text


def reference_to_markdown(ref):
    if "type" in ref:
        if ref["type"] == "inline":
            return False
    markdown_entry = ""

    # Füge den Titel als Markdown-Link hinzu, falls eine URL vorhanden ist, sonst nur den Titel
    # Verwende 'Unbekannter Titel', falls kein Titel vorhanden ist
    title = ref.get('title', 'Unbekannter Titel')
    if 'url' in ref:
        markdown_entry += f"[{title}]({ref['url']})"
    else:
        markdown_entry += title

    # Sammle zusätzliche Informationen in einer Liste
    details = []
    if 'newspaper' in ref:
        details.append(f"_{ref.get('newspaper', '')}_")
    if 'date' in ref:
        details.append(ref.get('date', ''))
    if 'page' in ref:
        details.append(f"p. {ref.get('page', '')}")
    if 'publisher' in ref:
        details.append(f"Publisher: {ref.get('publisher', '')}")
    if 'isbn' in ref:
        details.append(f"ISBN: {ref.get('isbn', '')}")
    if 'author-link' in ref:
        details.append(
            f"Author: [{ref.get('first', '')} {ref.get('last', '')}](https://en.wikipedia.org/wiki/{ref.get('author-link', '')})")
    elif 'first' in ref and 'last' in ref:
        details.append(f"Author: {ref.get('first', '')} {ref.get('last', '')}")

    # Verbinde die Details mit Kommas und füge sie dem Markdown-Eintrag hinzu
    if details:
        markdown_entry += " - " + ", ".join(details)

    return markdown_entry


def get_sources(section):
    sources = []
    if "references" in section:
        for reference in section["references"]:
            source = reference_to_markdown(reference)
            if source:
                sources.append(source)
    return sources


def process_json(data):
    output = {}

    main_images = get_images(data["sections"][0])
    main_images_object = transform_entries(main_images)

    for section in data["sections"]:
        date = convert_date_to_iso(section["title"])
        if date:
            if "lists" in section:
                for list in section["lists"]:
                    obj = {}
                    events, births, deaths = split_list_into_categories(list)
                    images = get_images(section)
                    sources = get_sources(section)

                    obj["events"] = [
                        {"text": object_to_markdown(event), "raw": event} for event in events]
                    obj["births"] = [
                        {"text": object_to_markdown(birth), "raw": birth} for birth in births]
                    obj["deaths"] = [
                        {"text": object_to_markdown(death), "raw": death} for death in deaths]
                    obj["images"] = images
                    obj["sources"] = sources

                    if date in main_images_object:
                        obj["images"] += main_images_object[date]

                    obj["date"] = date
                    output[date] = obj
    return output


def process_json_files(folder_path):
    results = {}  # Liste, um die Ergebnisse der angewandten Funktion zu speichern

    # Durchlaufe alle Dateien im angegebenen Ordner
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Überprüfe, ob die Datei eine JSON-Datei ist
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Wende die benutzerdefinierte Funktion auf die Daten an
                result = process_json(data)
                # Füge das Ergebnis zur results hinzu
                results.update(result)

    return results


if __name__ == "__main__":
    folder_path = "scraped"
    output = process_json_files(folder_path)

    with open('transform.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
