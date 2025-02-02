from openai import AsyncOpenAI
from config import Config
from entities import RSSEntry
import json
import asyncio


cfg = Config()
client = AsyncOpenAI(
    api_key=cfg.OPENAI_API_KEY
)

# 경제를 처음 접하는 사람들을 위해, 매일매일의 뉴스를 토대로 적절한 설명을 포함한 뉴스레터를 보내주려 합니다. 이런 데이터가 있을 때, 어떤 기준으로 분류하여 뉴스레터의 재료로 삼아야 할까요?

prompt = '''You are a newsletter editor who is creating a informatic article based on the daily economic news for beginners.
As I give you the already filtered news articles, please select the most appropriate article to describe the economic situation of the day.
Please return the index of the article you selected and the reason for your selection.

Respond with a JSON object in the following format:
{ "index": 0, "reason": "" }
'''

async def select_articles(item: RSSEntry) -> dict:
    list_of_article = "Articles Lists:\n".join([f"{i}. {item.title}" for i, item in enumerate(item)])

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": list_of_article
            }
        ],
        response_format={"type": "json_object"}
    )
    
    response = json.loads(response.choices[0].message.content)
    response['entry'] = item[response['index']]
    return response
