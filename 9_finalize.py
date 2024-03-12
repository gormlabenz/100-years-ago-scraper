import json
import re


def get_basename_from_url(url):
    """
    Extrahiert den Basenamen aus der URL, ohne den Namen zu verändern.
    """
    # Extrahiert den letzten Teil der URL nach dem letzten '/' als Dateinamen
    file_name = url.split('/')[-1]
    # Entfernt die Dateiendung, wenn vorhanden, ohne den Namen zu verändern
    base_name = file_name.rsplit('.', 1)[0]
    return base_name


def adjust_image_objects(image_obj):
    new_image_obj = {}
    if 'new_caption' in image_obj:
        new_image_obj['caption'] = image_obj['new_caption']
    if 'file' in image_obj:
        new_image_obj['file'] = get_basename_from_url(image_obj['url'])
    return new_image_obj


def process_json(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    images_dict = {}

    for date, details in data.items():
        if 'images' in details:
            for image in details['images']:
                if not image['file'].lower().endswith('.svg'):
                    images_dict[get_basename_from_url(
                        image['url'])] = f"../assets/images/{get_basename_from_url(image['url'])}.png"

        # Anpassungen hier...
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
