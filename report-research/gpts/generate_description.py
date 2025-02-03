from openai import AsyncOpenAI, BaseModel
from config import Config
from entities import RSSEntry
import json


cfg = Config()
client = AsyncOpenAI(
    api_key=cfg.OPENAI_API_KEY
)


# TODO: ~에요 사용해서 구어체로 작성하기. 직접적 경제 용어가 아닌 것들 (보복)은 필터링하기
prompt = '''안녕하세요, 당신은 지금 하루의 경제 소식을 정리하여 전달하기 위한 뉴스레터를 작성중인 경제 전문가입니다. 초심자를 위한 뉴스레터이므로, 분석한 여러 키워드 중 기업명이나 고유명사를 제외하고 설명이 필요한 키워드를 필터링해 주세요.
단어의 뜻이나, 반의어 등을 포함하여 아주 쉽고 구체적인 설명을 부탁드러요. 또한 구어체와 존대어를 사용해 주세요. (예: ~에요.)
그리고 각 키워드별로 제목 맨 앞에 들어갈 이모티콘 하나를 반환해 주세요. 의미와 맞는 이모티콘을 선택해 주세요.

Return the results in JSON format as follows:
[
    {"keyword": "", "description": "", "emoji": ""},
    {"keyword": "", "description": "", "emoji": ""}
]
'''


async def generate_description(keywords: list[str]) -> list[dict]:
    print("Generating descriptions for keywords:", keywords)
    print("Prompt:", prompt)
    print("Contents:", keywords)


    response = await client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": "키워드: " + str(keywords)
            }
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
