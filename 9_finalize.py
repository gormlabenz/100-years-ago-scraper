import json


def get_basename_from_url(url):
    """
    Extracts the base name from the URL without changing the name.
    """
    # Extracts the last part of the URL after the last '/' as the file name
    file_name = url.split('/')[-1]
    # Removes the file extension, if present, without changing the name
    base_name = file_name.rsplit('.', 1)[0]
    return base_name


def adjust_image_objects(image_obj):
    new_image_obj = {}
    if 'new_caption' in image_obj:
        new_image_obj['caption'] = image_obj['new_caption']
    if 'file' in image_obj:
        new_image_obj['file'] = get_basename_from_url(image_obj['url'])
    return new_image_obj


def remove_empty_entries_and_raw(entries):
    """
    Entfernt Einträge, deren 'text'-Eigenschaft leer ist und löscht 'raw'-Einträge.
    """
    # Entfernen der Einträge, deren 'text'-Eigenschaft leer ist
    filtered_entries = [entry for entry in entries if entry.get('text')]
    # Löschen der 'raw'-Einträge aus jedem verbleibenden Eintrag
    for entry in filtered_entries:
        if 'raw' in entry:
            del entry['raw']
    return filtered_entries


def process_json(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    images_dict = {}

    for date, details in data.items():
        # Bereinigung von leeren Einträgen und Löschen von 'raw' in births, deaths und events
        for category in ['births', 'deaths', 'events']:
            if category in details:
                details[category] = remove_empty_entries_and_raw(
                    details[category])

        if 'images' in details:
            for image in details['images']:
                if not image['file'].lower().endswith('.svg'):
                    images_dict[get_basename_from_url(
                        image['url'])] = f"../assets/images/{get_basename_from_url(image['url'])}.png"

        image_objects = details.get('images', [])
        image_objects = [
            img for img in image_objects if not img['file'].lower().endswith('.svg')]
        adjusted_images = [adjust_image_objects(img) for img in image_objects]
        details['images'] = adjusted_images

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    with open('Images.ts', 'w') as ts_file:
        ts_file.write('const images = {\n')
        for key, url in images_dict.items():
            if """'""" in key:
                key_string = f'"{key}"'
            else:
                key_string = f"'{key}'"
            ts_file.write(f"  {key_string}: require(\"{url}\"),\n")
        ts_file.write('};\n\nexport default images;\n')


if __name__ == "__main__":
    process_json('categories.json', 'data.json')
