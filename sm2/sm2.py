from enum import Enum
import random
import typing as t

from pydantic import BaseModel

from const import EASY_BONUS, GRADUATING_INTERVAL, INITIAL_INTERVALS, INITIAL_RELEARN_INTERVALS, \
    LAPSE_INTERVAL_MULTIPLIER, EASY_INTERVAL, DEFAULT_EASE
from dto import Choice, Phase, Card
from libs.interval_calculator import minute_to_interval


class SM2Result(BaseModel):
    phase: Phase
    step: t.Optional[int] = None
    ease: t.Optional[float] = None
    interval: t.Optional[float] = None
    leech: int = 0


DAY_IN_MINUTES = 1440

class SM2:
    hard_interval_multiplier: float
    _min_days: int
    _max_days: int
    learn_intervals: t.List[int]
    relearn_intervals: t.List[int]
    default_ease: float
    graduating_interval: int
    easy_interval: int
    easy_bonus: float

    @property
    def min_interval(self):
        return self._min_days * DAY_IN_MINUTES

    @property
    def max_interval(self):
        return self._max_days * DAY_IN_MINUTES

    def __init__(
        self,
        hard_interval_multiplier: float = 1.2,
        min_days: int = 1,
        max_days: int = 100 * 365,
        learn_intervals: t.List[int] = INITIAL_INTERVALS,
        relearn_intervals: t.List[int] = INITIAL_RELEARN_INTERVALS,
        default_ease: float = DEFAULT_EASE,
        graduating_interval: int = GRADUATING_INTERVAL,
        easy_interval: int = EASY_INTERVAL,
        easy_bonus: float = EASY_BONUS
    ):
        self.hard_interval_multiplier = hard_interval_multiplier
        self._min_days = min_days
        self._max_days = max_days
        self.learn_intervals = learn_intervals
        self.relearn_intervals = relearn_intervals
        self.default_ease = default_ease
        self.graduating_interval = graduating_interval
        self.easy_interval = easy_interval
        self.easy_bonus = easy_bonus

    @staticmethod
    def get_initial_intervals() -> t.List[str]:
        return INITIAL_INTERVALS

    @staticmethod
    def create_initial_card(name: str, description: str) -> Card:
        return Card(
            name=name,
            description=description,
        )

    def _handle_learning(self, card: Card, choice: Choice) -> SM2Result:
        """
        return the next step and interval for the card
        """
        step = card.step

        if choice == Choice.AGAIN:
            return SM2Result(phase=Phase.LEARNING, step=0, interval=INITIAL_INTERVALS[0], leech=card.leech + 1)
        elif choice == Choice.HARD:
            if step == 0 and len(self.learn_intervals) == 1:
                return SM2Result(phase=Phase.LEARNING, step=0, interval=int(self.learn_intervals[0] * 1.5))
            elif step == 0 and len(self.learn_intervals) > 1:
                return SM2Result(phase=Phase.LEARNING, step=0, interval=(self.learn_intervals[step] + self.learn_intervals[step+1]) / 2)

            return SM2Result(phase=Phase.LEARNING, step=step, interval=self.learn_intervals[step])
        elif choice == Choice.GOOD:
            if step + 1 == len(self.learn_intervals):
                return SM2Result(phase=Phase.EXPONENTIAL, step=None, ease=self.default_ease, interval=self.graduating_interval)

            return SM2Result(phase=Phase.LEARNING, step=step + 1, interval=self.learn_intervals[step+1])
        elif choice == Choice.EASY:
            return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=self.easy_interval)

    def _handle_exponential(self, card: Card, choice: Choice) -> SM2Result:
        ease = card.ease
        interval = card.interval
        rand_interval = random.randrange(0, 1441)

        if choice == Choice.AGAIN:
            ease = max(1.3, card.ease * (1 - 0.2))

            # TODO: add fuzz and argument -- new_interval parameter
            interval = max(interval * LAPSE_INTERVAL_MULTIPLIER, self.min_interval)

            if len(self.relearn_intervals) > 0:
                return SM2Result(phase=Phase.RELEARN, ease=ease, interval=self.relearn_intervals[0], step=0)

            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval, leech=card.leech + 1)
        elif choice == Choice.HARD:
            ease = max(1.3, card.ease * (1 - 0.15))
            interval = min(
                interval * self.hard_interval_multiplier,
                1440 * 36500 # 100 years
            )
            # TODO: days_overdue / 4
            # TODO: add fuzz to interval
            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval)
        elif choice == Choice.GOOD:
            interval = min(
                (interval + rand_interval) * ease,
                1440 * 36500 # 100 years
            )

            # TODO: fix random to fuzz interval
            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval)
        elif choice == Choice.EASY:
            ease = ease * 1.15
            interval = min(
                (interval + rand_interval) * ease * self.easy_bonus,
                1440 * 36500 # 100 years
            )

            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval)

    def _handle_relearn(self, card: Card, choice: Choice) -> SM2Result:
        step = card.step

        if len(self.relearn_intervals) == 0 or card.step >= len(self.relearn_intervals):
            interval = card.interval * card.ease
            return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=interval, ease=card.ease)

        if choice == Choice.AGAIN:
            return SM2Result(phase=Phase.RELEARN, step=0, interval=self.relearn_intervals[0], leech=card.leech + 1)
        elif choice == Choice.HARD:
            if step == 0 and len(self.relearn_intervals) == 1:
                return SM2Result(phase=Phase.RELEARN, step=0, interval=int(self.relearn_intervals[0] * 1.5))
            elif step == 0 and len(self.relearn_intervals) > 1:
                return SM2Result(phase=Phase.RELEARN, step=0, interval=(self.relearn_intervals[step] + self.relearn_intervals[step+1]) / 2)

            return SM2Result(phase=Phase.RELEARN, step=0, interval=self.relearn_intervals[step])
        elif choice == Choice.GOOD:
            if step + 1 == len(self.relearn_intervals):
                return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=card.interval * card.ease)

            return SM2Result(phase=Phase.RELEARN, step=step + 1, interval=self.relearn_intervals[step+1])
        elif choice == Choice.EASY:
            interval = min(
                card.interval * card.ease * self.easy_bonus,
                1440 * 36500 # 100 years
            )

            return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=interval)

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