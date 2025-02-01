from db import get_articles_by_korean_date
from rss import parse_feed
from entities import ArticleType, RSSEntry
from gpts import classify_rss_entries_async
import asyncio 
import pickle

# 5천개에 2.5달러? 나쁘지 않은데?
async def execute():
    feed_url = "https://feeds.content.dowjones.io/public/rss/mw_topstories"

    entries = parse_feed(feed_url)
    classified = await classify_rss_entries_async(entries)

    for entry, classification in zip(entries, classified):
        print(f"{entry.title} - {classification['classification']}")

        entry.article_type = ArticleType()


feed_urls = [
    "https://www.mk.co.kr/rss/30300018/",
    "https://www.mk.co.kr/rss/50300009/",
    "https://www.mk.co.kr/rss/50200011/",
    "https://www.mk.co.kr/rss/30100041/",
    "https://www.stlouisfed.org/rss/page%20resources/publications/blog-entries",
    "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "http://rss.cnn.com/rss/money_markets.rss",
    "https://rss.etoday.co.kr/eto/company_news.xml",
    "https://news.einfomax.co.kr/rss/S1N21.xml",
    "https://www.infostockdaily.co.kr/rss/allArticle.xml"
]


async def main():
    results = await get_articles_by_korean_date('2025-01-30')
    entries = [RSSEntry.from_db(row) for row in results]

    classified = await classify_rss_entries_async(entries)

    for entry, classification in zip(entries, classified):
        print(f"{entry.title} - {classification['classification']}")
        entry.article_type = ArticleType(classification['classification'])


    with open('classified.pkl', 'wb') as f:
        pickle.dump(entries, f)


if __name__ == "__main__":
    asyncio.run(main())
