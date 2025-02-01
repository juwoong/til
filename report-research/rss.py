import feedparser
from entities import RSSEntry

def parse_feed(url: str) -> list[RSSEntry]:
    result = feedparser.parse(url)
    items = []
    for entry in result.entries:
        items.append(
            RSSEntry.from_rss(entry)
        )
    return items
