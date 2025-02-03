from db import get_articles_by_korean_date
from gpts.generate_description import generate_description
from gpts.generate_questions import get_answers, get_question
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


async def get_article(date: datetime):
    results = await get_articles_by_korean_date(date.strftime('%Y-%m-%d'))
    entries = [RSSEntry.from_db(row) for row in results]

    classified = await classify_rss_entries_async(entries)

    for entry, classification in zip(entries, classified):
        print(f"{entry.title} - {classification['classification']}")
        entry.article_type = ArticleType(classification['classification'])

    return entries

def extract_results(results) -> list:
    # check object is single
    if not any([type(v) is list for v in results.values()]):
        return [results]

    if type(results) is dict and 'result' in results:
        return results['result']
    elif type(results) is dict and 'results' in results:
        return results['results']
    return results

async def get_most_important_news():
    now = datetime.now()
    entries = await get_article(now)

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

    questions = await get_question(selected['entry'])
    print("questions", questions)

    questions = extract_results(questions)
    answers = await get_answers(selected['entry'], [it.get('question') for it in questions if it.get('question')])
    answers = extract_results(answers)

    print("answers", answers)

    print("\n\n=================================\n\n")
    now_format = now.strftime('%Y년 %m월 %d일')

    print(f"**{now_format}의 초보자 경제 뉴스**")
    print(f"{remove_leading_bracket(selected['entry'].title)}\n\n")

    print(f"{summary['summary']}\n\n")

    print(f"**Q&A**")
    for answer in answers:
        print(f"Q: {answer['question']}\nA: {answer['answer']}\n\n")

    print(f"**용어 설명**")
    description = extract_results(description)
    for desc in description:
        print(f"{desc['emoji']} {desc['keyword']}\n{desc['description']}\n\n")


if __name__ == "__main__":
    asyncio.run(get_most_important_news())
