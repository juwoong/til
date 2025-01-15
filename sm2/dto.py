from pydantic import BaseModel
from enum import Enum
from datetime import datetime

from const import DEFAULT_EASE
import typing as t
import json 
import abc


class Choice(int, Enum):
    AGAIN = 0
    HARD = 1
    GOOD = 2
    EASY = 3

class Phase(int, Enum):
    NEW = 0
    LEARNING = 1
    EXPONENTIAL = 2
    RELEARN = 3


class AbstractModel(abc.ABC, BaseModel):
    @classmethod
    @abc.abstractmethod
    def from_sql(cls, row: tuple) -> 'AbstractModel':
        pass

    @abc.abstractmethod
    def to_sql(self) -> str:
        pass


class Data(AbstractModel):
    id: int
    question: str
    pronounciation: str
    meaning: str
    priority: int
    is_generated: bool


    @classmethod
    def from_sql(cls, row: tuple) -> 'Data':
        desc = json.loads(row[2])

        return cls(
            id=row[0],
            question=row[1],
            pronounciation=desc['pronunciation'],
            meaning=desc['meaning'],
            priority=row[3],
            is_generated=(row[4] == 1),
        )
    
    def to_sql(self) -> str:
        desc = json.dumps({
            'pronunciation': self.pronounciation,
            'meaning': self.meaning,
        })
        return f'INSERT INTO datas (question, description, priority, is_generated) VALUES (\'{self.question}\', \'{desc}\', {self.priority}, {int(self.is_generated)});'
    
    def update_sql(self) -> str:
        return f'UPDATE datas SET is_generated = {int(self.is_generated)} WHERE id = {self.id};'

class Card(AbstractModel):
    id: int = 0
    data_id: int
    phase: Phase = Phase.NEW
    interval: int = 0
    ease: float = DEFAULT_EASE
    step: int = 0  # disable when phase is exponential
    leech: int = 0
    last_review: t.Optional[datetime] = None
    next_review: t.Optional[datetime] = None
    data: Data = None

    @classmethod
    def from_sql(cls, row: tuple) -> 'Card':
        last_review = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S') if row[7] else None
        next_review = datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S') if row[8] else None

        return cls(
            id=row[0],
            data_id=row[1],
            phase=Phase(row[2]),
            interval=row[3],
            ease=row[4],
            step=row[5],
            leech=row[6],
            last_review=last_review,
            next_review=next_review,
        )

    def to_sql(self) -> str:
        last_review = f"\'{self.last_review.strftime('%Y-%m-%d %H:%M:%S')}\'" if self.last_review else 'NULL'
        next_review = f"\'{self.next_review.strftime('%Y-%m-%d %H:%M:%S')}\'" if self.next_review else 'NULL'

        return f'INSERT INTO cards(data_id, phase, interval, ease, step, leech, last_review, next_review) VALUES ({self.data_id}, {self.phase.value}, {self.interval}, {self.ease}, {self.step}, {self.leech}, {last_review}, {next_review});'
    
    def update_sql(self) -> str:
        last_review = f"\'{self.last_review.strftime('%Y-%m-%d %H:%M:%S')}\'" if self.last_review else 'NULL'
        next_review = f"\'{self.next_review.strftime('%Y-%m-%d %H:%M:%S')}\'" if self.next_review else 'NULL'

        return f'UPDATE cards SET phase = {self.phase.value}, interval = {self.interval}, ease = {self.ease}, step = {self.step}, leech = {self.leech}, last_review = {last_review}, next_review = {next_review} WHERE id = {self.id};'
