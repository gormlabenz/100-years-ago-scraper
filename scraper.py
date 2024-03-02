from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import json
from datetime import datetime, timedelta
import re


def generate_urls(start_year, start_month, end_year, end_month):
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1)

    urls = []
    while start_date <= end_date:
        urls.append(
            f"https://en.wikipedia.org/wiki/{start_date.strftime('%B_%Y')}")
        start_date += timedelta(days=31)  # Add a month (approximation)
        # Ensure it's the first day of the month
        start_date = start_date.replace(day=1)
    return urls


def clean_content(content):
    # Entfernen von Markdown-Links, um nur den Text zu behalten
    content = re.sub(r'^- ', '', content)
    # Entfernen von Verweisen auf Quellenangaben
    # Entfernt Verweise wie [#cite_note-1]
    content = re.sub(r'\[\#cite_note-[^\]]*\]', '', content)
    # Entfernt Zahlenverweise wie [1][2]
    content = re.sub(r'\[\d+\]', '', content)
    content = re.sub(r'\[\](?=\[|\]|$|\.|\,|\;|\:)', '',
                     content)  # Entfernt leere Klammern []
    # Zusätzliche Bereinigung für verbleibende Fälle
    # Für den Fall, dass Verweise in Klammern sind
    content = re.sub(r'\(\#cite_note-[^\)]*\)', '', content)
    content = re.sub(r'\[\]', '', content)
    content = content.replace("\\\"", "\"")
    return content.strip()


def convert_date_to_iso(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y (%A)")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def scrape_wikipedia_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        html_content = page.inner_html('body')
        browser.close()

    soup = BeautifulSoup(html_content, 'html.parser')
    events_data = []

    for headline in soup.find_all('h2'):
        date_text = headline.find('span', class_='mw-headline')
        if date_text:
            iso_date = convert_date_to_iso(date_text.text)
            next_node = headline.find_next_sibling()
            while next_node and next_node.name == 'ul':
                for li in next_node.find_all('li'):
                    # Entfernen von Quellenverweisen im Text
                    content_text = md(str(li), strip=['sup'])
                    # Entfernen von Listenzeichen, falls vorhanden
                    content_text = clean_content(content_text)
                    sources = []
                    for sup in li.find_all('sup', class_='reference'):
                        ref_link = sup.find('a')
                        if ref_link:
                            # Entfernen des '#' am Anfang
                            ref_id = ref_link.get('href')[1:]
                            citation = soup.find(id=ref_id)
                            if citation:
                                cite = citation.find('cite')
                                if cite:
                                    # Hinzufügen des kompletten Quellentextes inklusive URLs
                                    source_text = md(str(cite), strip=[])
                                    source_text = source_text.replace(
                                        "\\\"", "\"")
                                    sources.append(source_text)
                    events_data.append(
                        {'date': iso_date, 'content': content_text, 'sources': sources})
                next_node = next_node.find_next_sibling()

    return events_data


def main(start_year, start_month, end_year, end_month):
    urls = generate_urls(start_year, start_month, end_year, end_month)
    for url in urls:
        data = scrape_wikipedia_page(url)
        # Generieren des Dateinamens basierend auf der URL
        date_part = url.split('/')[-1]  # Extrahieren des Datums aus der URL
        filename = f'output/{date_part}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# Start- und Enddatum des Zeitraums festlegen
start_year = 1924
start_month = 2
end_year = 1925
end_month = 2

main(start_year, start_month, end_year, end_month)
