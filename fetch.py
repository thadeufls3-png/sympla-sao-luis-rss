import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

API_URL = "https://api.sympla.com.br/public/v3/events"

def fetch_events():
    events = []
    page = 1
    
    while True:
        r = requests.get(API_URL, params={"page": page})
        data = r.json()

        if "data" not in data or not data["data"]:
            break

        events.extend(data["data"])
        
        page += 1
    
    return events

def filter_sao_luis(events):
    return [
        e for e in events
        if e.get("address", {}).get("city", "").lower() == "são luís"
        and e.get("address", {}).get("state", "").lower() == "ma"
    ]

def build_rss(events):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Eventos em São Luís - Sympla"
    ET.SubElement(channel, "link").text = "https://www.sympla.com.br/eventos/sao-luis-ma"
    ET.SubElement(channel, "description").text = "Feed automático dos eventos da Sympla em São Luís"

    for e in events:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = e["name"]
        ET.SubElement(item, "link").text = e["url"]
        desc = e.get("description") or ""
        ET.SubElement(item, "description").text = desc

        start = e.get("start_date")
        if start:
            dt = datetime.fromisoformat(start.replace("Z",""))
            pub = dt.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
            ET.SubElement(item, "pubDate").text = pub
    
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)

def main():
    events = fetch_events()
    sao_luis = filter_sao_luis(events)
    xml = build_rss(sao_luis)
    with open("rss.xml", "wb") as f:
        f.write(xml)

if __name__ == "__main__":
    main()
