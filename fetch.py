import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

URL = "https://www.sympla.com.br/eventos/sao-luis-ma"

def fetch_events():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html"
    }

    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select("a.sympla-card")

    events = []

    for card in cards:
        name = card.get("data-name", "").strip()
        link = card.get("href", "")
        date_el = card.select_one(".qtfy416")
        date = date_el.text.strip() if date_el else ""

        venue_el = card.select_one(".pn67h1e")
        venue = venue_el.text.strip() if venue_el else ""

        img_el = card.select_one("img")
        img = img_el.get("src") if img_el else ""

        events.append({
            "name": name,
            "link": link,
            "date": date,
            "venue": venue,
            "image": img
        })

    return events

def build_rss(events):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Eventos Sympla — São Luís"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Feed automático dos eventos da Sympla em São Luís"

    for e in events:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = e["name"]
        ET.SubElement(item, "link").text = e["link"]
        ET.SubElement(item, "description").text = f"{e['date']} — {e['venue']}"
        ET.SubElement(item, "pubDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)

def main():
    events = fetch_events()
    rss = build_rss(events)
    with open("rss.xml", "wb") as f:
        f.write(rss)

if __name__ == "__main__":
    main()
