import json
import openai
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI API Key einrichten
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_new_caption(date, events_text, file, old_caption):
    """
    Generiert eine neue Bildunterschrift, wenn nötig.
    """
    # API-Aufruf, um die neue Bildunterschrift zu generieren
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You write new captions for images. The caption could:\n- Provide information about what the coressponding news item is\n- Provide information about the motif, if this is clear from the old caption\n- Have the sound of a news headline\n\nThere must be no dates or descriptions such as \"Caption:\" in the caption"
            },
            {
                "role": "user",
                "content": f"{date}\n\nNews:\n{events_text}\n\nGenerate caption for this image:\nFile: {file}\nCaption: {old_caption}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message['content'].replace("Caption:", "").replace("Headline:", "").replace("\"", "").strip()


def update_json_with_new_captions(input_json_path, output_json_path):
    """
    Liest das Eingabe-JSON und generiert neue Bildunterschriften für jedes Bild.
    """
    # JSON einlesen
    with open(input_json_path, 'r') as file:
        data = json.load(file)

    # Fortschrittsanzeige mit tqdm
    for date, details in tqdm(data.items(), desc="Generiere neue Bildunterschriften"):
        if 'images' in details:
            # Alle Event-Texte des Tages sammeln für den Kontext
            events_text = "\n\n-".join([f"{event['headline']}\n{event['raw']['text']}"
                                        for event in details['events']])
            for image in details['images']:
                # Neue Bildunterschrift generieren
                new_caption = generate_new_caption(
                    date, events_text, image['file'], image['caption'])
                # Bildunterschrift aktualisieren
                image['new_caption'] = new_caption

                # Aktualisiertes JSON in neuer Datei speichern
                with open(output_json_path, 'w') as file:
                    json.dump(data, file, indent=4)

    print("Aktualisierung abgeschlossen. Das aktualisierte JSON wurde gespeichert.")


if __name__ == "__main__":
    # Anpassen an den tatsächlichen Pfad
    input_json_path = 'push_notifications.json'
    # Pfad für das aktualisierte JSON
    output_json_path = 'captions.json'
    update_json_with_new_captions(input_json_path, output_json_path)
