import requests
import json
import os

# Angenommen, dies ist Ihr JSON-String
with open('captions.json', 'r') as file:
    data = json.load(file)

# Ein Verzeichnis für die heruntergeladenen Bilder erstellen, falls es noch nicht existiert
os.makedirs('images', exist_ok=True)

headers = {
    'User-Agent': '100-Years-Ago-App/1.0 (gorm@labenz.io)'
}

# Über das JSON-Objekt iterieren
for date, details in data.items():
    if 'images' in details:
        for image in details['images']:
            image_url = image['url']
            # Den Dateinamen aus der URL extrahieren
            filename = image_url.split('/')[-1]
            # Vollständigen Pfad für die gespeicherte Datei erstellen
            filepath = os.path.join('images', filename)

            # Bild herunterladen und speichern
            response = requests.get(image_url, headers=headers)
            if response.status_code == 200:
                with open(filepath, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {filename}")
                print(
                    f"Status code: {response.status_code}, Reason: {response.reason}")

print("Download completed.")
