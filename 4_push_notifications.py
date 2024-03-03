import json
import openai
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI API Key einrichten
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_push_notification(date, events):
    """
    Generiert den Text für eine Push-Benachrichtigung basierend auf den Nachrichten eines Tages.
    """
    # Nachrichtentexte zusammenfügen
    events_text = "\n\n".join(
        [f"{event['headline']}\n{event['raw']['text']}" for event in events])

    # API-Aufruf, um die Push-Benachrichtigung zu generieren
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """You are responsible for writing the text for mobile push notifications. These texts should summarize the most important news of the day and be composed in a formal, flowing text style. It is extremely important that you do not use emojis, hashtags, or common phrases like "Stay informed!" or "Don't miss the latest news!". Please also avoid introductory phrases such as "Breaking:", "On this day:", or similar. The text should directly and factually convey the message without using unnecessary attention-grabbers."""
            },
            {
                "role": "user",
                "content": f"{date}\n\n{events_text}"
            }
        ],
        temperature=0.6,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message['content'].strip('- ').replace('\n- ', '; ').strip()


def update_json_with_push_notifications(input_json_path, output_json_path):
    """
    Liest das Eingabe-JSON und generiert Push-Benachrichtigungen für jeden Tag.
    """
    # JSON einlesen
    with open(input_json_path, 'r') as file:
        data = json.load(file)

    # Fortschrittsanzeige mit tqdm
    for date in tqdm(data.keys(), desc="Generiere Push-Benachrichtigungen"):
        events = data[date]['events']
        # Push-Benachrichtigung für den Tag generieren
        push_notification = generate_push_notification(date, events)
        # Push-Benachrichtigung zu den Tagesdetails hinzufügen
        data[date]['push_notification'] = {
            "title": "100 Years Ago…", "text": push_notification}

        # Aktualisiertes JSON in neuer Datei speichern
        with open(output_json_path, 'w') as file:
            json.dump(data, file, indent=2)

    print("Aktualisierung abgeschlossen. Das aktualisierte JSON wurde gespeichert.")


if __name__ == "__main__":
    # Anpassen an den tatsächlichen Pfad
    input_json_path = 'headlines.json'
    # Pfad für das aktualisierte JSON
    output_json_path = 'push_notifications.json'
    update_json_with_push_notifications(input_json_path, output_json_path)
