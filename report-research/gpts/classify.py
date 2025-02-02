from openai import AsyncOpenAI
from config import Config
from entities import RSSEntry
import json
import asyncio


cfg = Config()
client = AsyncOpenAI(
    api_key=cfg.OPENAI_API_KEY
)

prompt = '''You are a classifier model trained to categorize economic and financial news articles for use in a daily economic summary.

Classify the following article into one of the three categories:
- critical_event: A market shock or unexpected event significantly impacting financial markets, such as a sudden stock drop due to unforeseen issues.
- trends: A notable but expected economic trend or policy change, such as an interest rate adjustment after months of decline.
- non_necessary: An article that is promotional, repetitive, or lacks meaningful economic insight.

Respond with a JSON object in the following format:
{ "classification": "" }
'''

async def classify_rss_entry_async(item: RSSEntry) -> dict:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            item.to_gpt_message()
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


async def classify_rss_entries_async(items: list[RSSEntry]) -> list[dict]:
    results = await asyncio.gather(*[classify_rss_entry_async(item) for item in items])
    return results
