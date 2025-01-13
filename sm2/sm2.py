from enum import Enum
import random
import typing as t

from pydantic import BaseModel

from const import EASY_BONUS, FIRST_EXPONENTIAL_INTERVAL, INITIAL_INTERVALS, INITIAL_RELEARN_INTERVALS, LAPSE_INTERVAL_MULTIPLIER
from dto import Choice, Phase, Card
from libs.interval_calculator import minute_to_interval


class SM2Result(BaseModel):
    phase: Phase
    step: t.Optional[int] = None
    ease: t.Optional[float] = None
    interval: t.Optional[int] = None


class SM2:
    @staticmethod
    def get_initial_intervals() -> t.List[str]:
        return INITIAL_INTERVALS

    @staticmethod
    def create_initial_card(name: str, description: str) -> Card:
        return Card(
            name=name,
            description=description,
        )

    @staticmethod
    def _handle_learning(card: Card, choice: Choice) -> SM2Result:
        """
        return the next step and interval for the card
        """
        step = card.step

        if choice == Choice.AGAIN:
            return SM2Result(phase=Phase.LEARNING, step=0, interval=INITIAL_INTERVALS[0])
        elif choice == Choice.HARD:
            if step == 0:
                return SM2Result(phase=Phase.LEARNING, step=0, interval=6)
            if step == 1:
                return SM2Result(phase=Phase.LEARNING, step=0, interval=INITIAL_INTERVALS[step])
            if step == 3:
                return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=INITIAL_INTERVALS[1])
            return SM2Result(phase=Phase.LEARNING, step=step, interval=INITIAL_INTERVALS[step+1])
        elif choice == Choice.GOOD:
            if step == 0:
                return SM2Result(phase=Phase.LEARNING, step=1, interval=INITIAL_INTERVALS[1])
            if step == 3:
                return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=FIRST_EXPONENTIAL_INTERVAL)
            return SM2Result(phase=Phase.LEARNING, step=step + 1, interval=INITIAL_INTERVALS[step+1])
        elif choice == Choice.EASY:
            return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=FIRST_EXPONENTIAL_INTERVAL)

    @staticmethod
    def _handle_exponential(card: Card, choice: Choice) -> SM2Result:
        ease = card.ease
        interval = card.interval
        rand_interval = random.randrange(0, 1441)

        if choice == Choice.AGAIN:
            return SM2Result(phase=Phase.RELEARN, ease=ease - 0.2, interval=int(interval * LAPSE_INTERVAL_MULTIPLIER), step=0)
        elif choice == Choice.HARD:
            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease - 0.15, interval=int(interval * 1.2))
        elif choice == Choice.GOOD:
            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=int((interval + rand_interval) * ease))
        elif choice == Choice.EASY:
            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease + 0.15, interval=int((interval + rand_interval) * (ease * EASY_BONUS)))

    @staticmethod
    def _handle_relearn(card: Card, choice: Choice) -> SM2Result:
        step = card.step

        if choice == Choice.AGAIN:
            return SM2Result(phase=Phase.RELEARN, step=0, interval=INITIAL_RELEARN_INTERVALS[0])
        elif choice == Choice.HARD:
            return SM2Result(phase=Phase.RELEARN, step=step, interval=INITIAL_RELEARN_INTERVALS[step+1] / 2)
        elif choice == Choice.GOOD:
            return SM2Result(phase=Phase.RELEARN, step=step + 1, interval=INITIAL_RELEARN_INTERVALS[step+1])
        elif choice == Choice.EASY:
            return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=INITIAL_RELEARN_INTERVALS[-1] + FIRST_EXPONENTIAL_INTERVAL)

    @staticmethod
    def get_next_card(card, choice) -> SM2Result:
        phase = card.phase

        if phase == Phase.LEARNING:
            return SM2._handle_learning(card, choice)
        elif phase == Phase.EXPONENTIAL:
            return SM2._handle_exponential(card, choice)
        elif phase == Phase.RELEARN:
            return SM2._handle_relearn(card, choice)

    @staticmethod
    def expected_interval(card: Card) -> t.List[str]:
        """
        return the expected interval for the card
        """
        intervals = []

        for choice in Choice:
            result = SM2.get_next_card(card, choice)
            intervals.append(minute_to_interval(result.interval))

        return intervals