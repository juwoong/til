from openai import AsyncOpenAI, BaseModel
from config import Config
from entities import RSSEntry
import json


cfg = Config()
client = AsyncOpenAI(
    api_key=cfg.OPENAI_API_KEY
)


prompt = '''Hello, you are an economic expert writing a daily newsletter summarizing key financial news. I will provide you with pre-filtered, meaningful news headlines, articles, and the reasoning behind their selection. Your task is to:
1.	Extract the most important points and summarize them in no more than three concise sentences.
2.	Generate a list of relevant, search-friendly tags to help track related developments in the future.
3.	Consider the provided selection criteria when determining key points and tags.
4.	Avoid including peripheral details that are not crucial to the core news.

Return the results in JSON format as follows:
{
  "summary": "Concise and essential summary of the news in up to three sentences.",
  "tags": ["Relevant", "Search-friendly", "Keywords", "For", "Tracking"]
}
'''

class SummaryRequest(BaseModel):
    reason: str
    entry: RSSEntry


async def get_summary(item: SummaryRequest) -> dict:
    message = f"title: {item.entry.title}\nreason: {item.reason}\ncontent: {item.entry.description}"

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": message
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
