import json
import openai
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI API Key einrichten
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_headline(date, event_text):
    """
    Generiert eine Schlagzeile für ein gegebenes Ereignis.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You write very short newspaper headlines. The headlines shouldn't be longer than a few words. The date isn't included in the headline. You only reply with the headline."
            },
            {
                "role": "user",
                "content": f"{date}\n{event_text}"
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message['content'].strip(' "\'')


def update_json_with_headlines(input_json_path, output_json_path):
    """
    Liest das Eingabe-JSON, generiert Schlagzeilen für neue Ereignisse und speichert das aktualisierte JSON separat.
    """
    # JSON einlesen
    with open(input_json_path, 'r') as file:
        data = json.load(file)

    # Fortschrittsanzeige mit tqdm
    for date in tqdm(data.keys(), desc="Verarbeite Daten"):
        details = data[date]
        for event in details['events']:
            # Überspringen, wenn Headline bereits vorhanden ist
            if 'headline' in event:
                continue

            # Headline für jedes neue Ereignis generieren
            headline = generate_headline(date, event['raw']['text'])
            event['headline'] = headline

            # Aktualisiertes JSON in neuer Datei speichern
            with open(output_json_path, 'w') as file:
                json.dump(data, file, indent=2)

    print("Aktualisierung abgeschlossen. Das aktualisierte JSON wurde gespeichert.")


if __name__ == "__main__":
    # Anpassen an den tatsächlichen Pfad
    input_json_path = 'headlines.json'
    # Pfad für das aktualisierte JSON
    output_json_path = 'headlines_2.json'
    update_json_with_headlines(input_json_path, output_json_path)
