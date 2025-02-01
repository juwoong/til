from rss import parse_feed
from entities import RSSEntry
from gpts import classify_rss_entries_async
import asyncio 

# 5천개에 2.5달러? 나쁘지 않은데?
async def main():
    feed_url = "https://feeds.content.dowjones.io/public/rss/mw_topstories"

    entries = parse_feed(feed_url)
    classified = await classify_rss_entries_async(entries)

    print("Classified entries:", classified)

    for entry, classification in zip(entries, classified):
        print(f"{entry.title} - {classification['classification']}")



if __name__ == "__main__":
    asyncio.run(main())
