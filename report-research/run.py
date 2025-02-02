from db import get_articles_by_korean_date
from gpts.generate_description import generate_description
from gpts.generate_summary import SummaryRequest, get_summary
from rss import parse_feed
from entities import ArticleType, RSSEntry
from gpts.classify import classify_rss_entries_async
from gpts.select_article import select_articles
import asyncio 
import pickle
from datetime import datetime

import re

def remove_leading_bracket(s: str) -> str:
    return re.sub(r'^[\(\[].*?[\)\]]\s*', '', s)

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


async def get_most_important_news():
    with open('classified.pkl', 'rb') as f:
        entries = pickle.load(f)

    important_news = [entry for entry in entries if entry.article_type != ArticleType.NON_NECESSARY]
    selected = await select_articles(important_news)

    print(selected)

    summary_request = SummaryRequest(
        reason=selected.get("reason"),
        entry=selected.get("entry"),
    )

    summary = await get_summary(summary_request)
    print(summary)

    description = await generate_description(summary.get("tags"))
    print(description)

    print("\n\n=================================\n\n")
    now = datetime.now().strftime('%Y년 %m월 %d일')

    print(f"**{now}의 초보자 경제 뉴스**")
    print(f"{remove_leading_bracket(selected['entry'].title)}\n\n")

    print(f"{summary['summary']}\n\n")

    print(f"**용어 설명**")
    if type(description) is dict and 'result' in description:
        description = description['result']
    elif type(description) is dict and 'results' in description:
        description = description['results']
    
    for desc in description:
        print(f"{desc['emoji']} {desc['keyword']}\n{desc['description']}\n\n")


if __name__ == "__main__":
    asyncio.run(get_most_important_news())
