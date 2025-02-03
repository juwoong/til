from openai import AsyncOpenAI, BaseModel
from config import Config
from entities import RSSEntry
import json


cfg = Config()
client = AsyncOpenAI(
    api_key=cfg.OPENAI_API_KEY
)


# TODO: ~에요 사용해서 구어체로 작성하기
prompt = '''안녕하세요, 당신은 지금 하루의 경제 소식을 정리하여 전달하기 위한 뉴스레터를 작성중인 경제 전문가입니다. 이미 유의미하다 필터링된 뉴스의 제목과 본문, 그리고 선정 이유를 제공하면, 중요한 항목을 정리하여 요약을 작성하고, 추후 사건을 다시 검색하기 쉽도록 하는 적절한 태그의 리스트를 작성하여 json 포맷으로 반환 해 주세요. 다만 핵심 내용과 조금 거리가 먼 부가 정보는 필터링해 주세요.
요약은 경제 초심자들이 쉽게 이해할 수 있도록 중요한 내용을 위주로 작성하고, 최대한 풀어서 설명해 주세요. 또한 구어체로 작성해 주시면 감사하겠습니다.
태그 또한 한글로 작성해 주세요.

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
    message = f"제목: {item.entry.title}\n선택 근거: {item.reason}\n뉴스 본문: {item.entry.description}"

    print("Generating Summary for article")
    print("Prompt:", prompt)
    print("Contents:", message)


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
