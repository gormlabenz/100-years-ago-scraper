import json
import re


def adjust_image_objects(image_obj):
    # Anpassung der Image-Objekte
    new_image_obj = {}
    if 'new_caption' in image_obj:
        new_image_obj['caption'] = image_obj['new_caption']
    if 'file' in image_obj:
        base_name = re.sub(r'File:', '', image_obj['file']).rsplit('.', 1)[0]
        new_image_obj['url'] = f"/assets/images/{base_name}.png"
    return new_image_obj


def process_json(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for date, details in data.items():
        # Entfernung des raw Entries aus den Events
        for event in details.get('events', []):
            if 'raw' in event:
                del event['raw']

        # Entfernung aller Image Entries, bei denen das Bild ein SVG ist
        images = details.get('images', [])
        images = [img for img in images if not img['file'].lower().endswith('.svg')]

        # Anpassung der Image Objekte
        adjusted_images = [adjust_image_objects(img) for img in images]
        details['images'] = adjusted_images

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    process_json('captions.json', 'output.json')
