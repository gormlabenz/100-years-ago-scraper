import json
import openai
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI API Key einrichten
openai.api_key = os.getenv("OPENAI_API_KEY")


def categorize_event(event_text):
    """
    Ordnet ein Ereignis einer oder mehreren Kategorien zu.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Your task is to assign events to one or more categories. It is extremely important that the assigned categories correspond exclusively to the categories from the list and that your response is a JSON list.\n\nPossible catgories:\n[\n    \"Science and Technology\",\n    \"Automotive Innovations\",\n    \"Political Movements\",\n    \"Military Engagements\",\n    \"Academic Achievements\",\n    \"Laws and Regulations\",\n    \"Cultural Openings\",\n    \"Economy and Labor\",\n    \"Diplomacy and Relations\",\n    \"Sports Competitions\",\n    \"Media and Publications\",\n    \"Health and Medicine\",\n    \"Environment and Conservation\",\n    \"Spiritual Events\",\n    \"Scientific Inventions\"\n]\n"
            },
            {
                "role": "user",
                "content": f"Choose one or more categories for this event:\n\n{event_text}\n\nPossible categories:\n[\n    \"Science and Technology\",\n    \"Automotive Innovations\",\n    \"Political Movements\",\n    \"Military Engagements\",\n    \"Academic Achievements\",\n    \"Laws and Regulations\",\n    \"Cultural Openings\",\n    \"Economy and Labor\",\n    \"Diplomacy and Relations\",\n    \"Sports Competitions\",\n    \"Media and Publications\",\n    \"Health and Medicine\",\n    \"Environment and Conservation\",\n    \"Spiritual Events\",\n    \"Scientific Inventions\"\n]\n"
            }
        ],
        temperature=0.3,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    categories = json.loads(response.choices[0].message['content'])
    return categories


def update_json_with_categories(input_json_path, output_json_path):
    """
    Liest das Eingabe-JSON, ordnet Ereignisse Kategorien zu und speichert das aktualisierte JSON separat.
    """
    # JSON einlesen
    with open(input_json_path, 'r') as file:
        data = json.load(file)

    # Fortschrittsanzeige mit tqdm
    for date in tqdm(data.keys(), desc="Verarbeite Daten"):
        details = data[date]
        for event in details['events']:
            # Überspringen, wenn Kategorien bereits vorhanden sind
            if 'categories' in event:
                continue

            # Kategorien für jedes neue Ereignis generieren
            categories = categorize_event(event['raw']['text'])
            event['categories'] = categories

            # Aktualisiertes JSON in neuer Datei speichern
            with open(output_json_path, 'w') as file:
                json.dump(data, file, indent=2)

    print("Aktualisierung abgeschlossen. Das aktualisierte JSON wurde gespeichert.")


if __name__ == "__main__":
    # Anpassen an den tatsächlichen Pfad
    input_json_path = 'categories.json'
    # Pfad für das aktualisierte JSON
    output_json_path = 'categories.json'
    update_json_with_categories(input_json_path, output_json_path)
