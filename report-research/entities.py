from pydantic import BaseModel
from datetime import datetime
from libs.times import struct_time_to_datetime 
from enum import Enum
import typing as t


class ArticleType(str, Enum):
    CRITICAL = "critical_event"
    TRENDS = "trends"
    NON_NECESSARY = "non_necessary"


class RSSEntry(BaseModel):
    title: str
    description: str 
    origin_content: t.Optional[str] = None
    published_at: datetime
    link: str

    article_type: t.Optional[ArticleType] = None

    @classmethod
    def from_rss(cls, entry: dict) -> 'RSSEntry':
        return cls(
            title=entry['title'],
            description=entry['summary'],
            published_at=struct_time_to_datetime(entry['published_parsed']),
            link=entry['link']
        )
    
    @classmethod
    def from_db(cls, row: dict) -> 'RSSEntry':
        return cls(
            title=row['title'],
            description=row['summary'],
            origin_content=row['original_content'],
            published_at=row['published_at'],
            link=row['url'],        )
    
    def to_gpt_message(self) -> dict:
        # return {
        #     "role": "user",
        #     "content": f"title: {self.title}\ndescription: {self.description}"
        # }
        return {
            "role": "user",
            "content": f"title: {self.title}",
        }
    
