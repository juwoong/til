import math
from datetime import datetime
import random
import typing as t

from pydantic import BaseModel

from const import EASY_BONUS, GRADUATING_INTERVAL, INITIAL_INTERVALS, INITIAL_RELEARN_INTERVALS, \
    LAPSE_INTERVAL_MULTIPLIER, EASY_INTERVAL, DEFAULT_EASE, DEFAULT_INTERVAL_MODIFIER
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
    interval_modifier: float

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
        easy_bonus: float = EASY_BONUS,
        interval_modifier: float = DEFAULT_INTERVAL_MODIFIER,
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
        self.interval_modifier = interval_modifier

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

        if choice == Choice.AGAIN:
            ease = max(1.3, card.ease * (1 - 0.2))

            interval = max(interval * LAPSE_INTERVAL_MULTIPLIER, self.min_interval)
            interval = self._get_fuzzed_interval(interval)

            if len(self.relearn_intervals) > 0:
                return SM2Result(phase=Phase.RELEARN, ease=ease, interval=self.relearn_intervals[0], step=0)

            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval, leech=card.leech + 1)
        elif choice == Choice.HARD:
            ease = max(1.3, card.ease * (1 - 0.15))
            day_adjustment = self._get_overdue_parameter(card, choice)

            interval = min(
                (interval + day_adjustment) * self.hard_interval_multiplier * self.interval_modifier,
                self.max_interval
            )
            # TODO: days_overdue / 4
            # TODO: add fuzz to interval
            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval)
        elif choice == Choice.GOOD:
            day_adjustment = self._get_overdue_parameter(card, choice)
            print("day_adjustment", day_adjustment)
            interval = min(
                (interval + day_adjustment) * ease * self.interval_modifier,
                self.max_interval,
            )
            print("interval", interval)
            interval = self._get_fuzzed_interval(interval)
            print("fuzzed", interval)

            # TODO: fix random to fuzz interval
            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval)
        elif choice == Choice.EASY:
            ease = ease * 1.15
            day_adjustment = self._get_overdue_parameter(card, choice)
            interval = min(
                (interval + day_adjustment) * ease * self.easy_bonus * self.interval_modifier,
                self.max_interval,
            )
            interval = self._get_fuzzed_interval(interval)

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

    def get_next_card(self, card, choice) -> SM2Result:
        phase = card.phase

        if phase == Phase.LEARNING:
            return self._handle_learning(card, choice)
        elif phase == Phase.EXPONENTIAL:
            return self._handle_exponential(card, choice)
        elif phase == Phase.RELEARN:
            return self._handle_relearn(card, choice)

    def expected_interval(self, card: Card) -> t.List[str]:
        """
        return the expected interval for the card
        """
        intervals = []

        for choice in Choice:
            result = self.get_next_card(card, choice)
            intervals.append(minute_to_interval(result.interval))

        return intervals

    def _get_fuzzed_interval(self, interval: float) -> float:
        interval_as_day = interval / DAY_IN_MINUTES

        if interval_as_day < 2.5:
            return interval

        def _get_fuzz_range(interval: float) -> t.Tuple[int, int]:
            fuzz_ranges = [
                {
                    "start": 2.5,
                    "end": 7.0,
                    "factor": 0.15,
                },
                {
                    "start": 7.0,
                    "end": 20.0,
                    "factor": 0.1,
                },
                {
                    "start": 20.0,
                    "end": math.inf,
                    "factor": 0.05,
                }
            ]

            delta = 1.0
            for fuzz_range in fuzz_ranges:
                delta += fuzz_range["factor"] * max(
                    min(interval, fuzz_range["end"]) - fuzz_range["start"], 0.0
                )

            min_interval = int(round(interval - delta))
            max_interval = int(round(interval + delta))

            min_interval = max(2, min_interval)
            max_interval = max(max_interval, self._max_days)
            min_interval = min(min_interval, max_interval)
            return min_interval, max_interval

        min_interval, max_interval = _get_fuzz_range(interval_as_day)

        fuzzed_interval_days = (
            random.random() * (max_interval - min_interval + 1) + min_interval
        )

        fuzzed_interval = min(
            round(fuzzed_interval_days * DAY_IN_MINUTES),
            self.max_interval
        )

        return fuzzed_interval

    @staticmethod
    def _get_overdue_parameter(card: Card, choice: Choice) -> float:
        if choice == Choice.AGAIN:
            return 0.0

        if card.last_review is None:
            return 0.0

        now = datetime.now()
        diff_days = (now - card.last_review).days

        if diff_days < 1:
            return 0.0

        hardness_divider = [0, 4, 2, 1]

        return diff_days / hardness_divider[choice.value]

