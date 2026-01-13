import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

GRAPHQL_URL = "https://discovery-next.svc.sympla.com.br/graphql"

def fetch_events():
    query = {
        "operationName": "SearchEvents",
        "variables": {
            "query": "",
            "page": 1,
            "city": "São Luís",
            "state": "MA",
            "size": 50,
            "sort": "date_asc"
        },
        "query": """
        query SearchEvents($query: String!, $page: Int!, $city: String, $state: String, $size: Int!, $sort: String) {
            search(query: $query, page: $page, city: $city, state: $state, size: $size, sort: $sort) {
                total
                events {
                    name
                    url
                    startDate
                    description
                    venue {
                        name
                        city
                        state
                    }
                }
            }
        }
        """
    }

    r = requests.post(GRAPHQL_URL, json=query)
    data = r.json()
    return data["data"]["search"]["events"]

def shorten(text, length=160):
    if not text:
        return ""
    text = text.strip().replace("\n", " ")
    return (text[:length] + "...") if len(text) > length else text

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

        # descrição curta
        desc = shorten(e.get("description", ""))
        ET.SubElement(item, "description").text = desc

        # pubDate
        start = e.get("startDate")
        if start:
            dt = datetime.fromisoformat(start.replace("Z", ""))
            pub = dt.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
            ET.SubElement(item, "pubDate").text = pub

    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)

def main():
    events = fetch_events()
    rss = build_rss(events)
    with open("rss.xml", "wb") as f:
        f.write(rss)

if __name__ == "__main__":
    main()
