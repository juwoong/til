from pydantic import BaseModel
from enum import Enum
from datetime import datetime

from const import DEFAULT_EASE
import typing as t


class Choice(int, Enum):
    AGAIN = 0
    HARD = 1
    GOOD = 2
    EASY = 3

class Phase(int, Enum):
    NEW = -1
    LEARNING = 0
    EXPONENTIAL = 1
    RELEARN = 2

class Card(BaseModel):
    id: int = 0
    name: str
    description: str
    interval: int = -1
    ease: float = DEFAULT_EASE
    phase: Phase = Phase.LEARNING
    step: int = 0  # disable when phase is exponential
    leech: int = 0
    last_review: t.Optional[datetime] = None
    next_review: t.Optional[datetime] = None
