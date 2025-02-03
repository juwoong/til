from typing import List
from openai import AsyncOpenAI, BaseModel
from config import Config
from entities import RSSEntry
import json


cfg = Config()
client = AsyncOpenAI(
    api_key=cfg.OPENAI_API_KEY
)


# TODO: ~에요 사용해서 구어체로 작성하기 / 질문 separate 할 수 있도록 만들기
question_prompt = '''안녕하세요, 당신은 경제를 배우고 싶어하지만, 경제에 대해서 아는 것이 거의 없는 초심자입니다. 저는 초심자를 대상으로 하는 경제 뉴스레터를 만드는 중이지만, 초심자들의 눈높이에서 어려워 할 만한 질문을 찾는 것이 어렵습니다.
제가 제시한 뉴스 기사를 읽고, 초심자들이 물어볼 만한 질문의 리스트를 만들어 주세요. 하나밖에 없더라도 결과는 리스트여야만 합니다! 질문은 가능한 한 쉽고 명확하게 작성해 주세요.

다음 데이터를 순수한 JSON 배열([])로 반환하세요. 
JSON 객체({})로 감싸지 말고, 최상위 구조가 배열이 되도록 하세요
결과는 다음과 같은 형태여야 합니다.
```json
[
    {"question": ""}
]
```
'''

# TODO: ~에요 사용해서 구어체로 작성하기
answer_prompt = '''안녕하세요, 당신은 지금 하루의 경제 소식을 정리하여 전달하기 위한 뉴스레터를 작성중인 경제 전문가입니다. 당신이 선정한 뉴스 기사를 보고 초심자들이 한 질문들에 대한 답변을 작성해 주세요. 

다음 데이터를 순수한 JSON 배열([])로 반환하세요. 
JSON 객체({})로 감싸지 말고, 최상위 구조가 배열이 되도록 하세요
결과는 다음과 같은 형태여야 합니다.
```json
[
    {"question": "", "answer": ""}
]
```
'''

async def get_question(entry: RSSEntry) -> dict:
    message = f"제목: {entry.title}\n뉴스 본문: {entry.description}"

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": question_prompt
            },
            {
                "role": "user",
                "content": message
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


async def get_answers(entry: RSSEntry, questions: List[str]) -> dict:
    message = f"제목: {entry.title}\n뉴스 본문: {entry.description}\n질문: " + "\n".join([f"{i}. {question}" for i, question in enumerate(questions, 1)])

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": answer_prompt
            },
            {
                "role": "user",
                "content": message
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
