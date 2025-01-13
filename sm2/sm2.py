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
            if step == 0 and len(INITIAL_INTERVALS) == 1:
                return SM2Result(phase=Phase.LEARNING, step=0, interval=int(INITIAL_INTERVALS[0] * 1.5))
            elif step == 0 and len(INITIAL_INTERVALS) > 1:
                return SM2Result(phase=Phase.LEARNING, step=0, interval=(INITIAL_INTERVALS[step] + INITIAL_INTERVALS[step+1]) / 2)

            return SM2Result(phase=Phase.LEARNING, step=step, interval=INITIAL_INTERVALS[step])
        elif choice == Choice.GOOD:
            if step + 1 == len(INITIAL_INTERVALS):
                return SM2Result(phase=Phase.EXPONENTIAL, step=None, ease=DEFAULT_EASE, interval=GRADUATING_INTERVAL)

            return SM2Result(phase=Phase.LEARNING, step=step + 1, interval=INITIAL_INTERVALS[step+1])
        elif choice == Choice.EASY:
            return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=EASY_INTERVAL)

    @staticmethod
    def _handle_exponential(card: Card, choice: Choice) -> SM2Result:
        ease = card.ease
        interval = card.interval
        rand_interval = random.randrange(0, 1441)

        if choice == Choice.AGAIN:
            ease = max(1.3, card.ease * (1 - 0.2))

            # TODO: add fuzz and argument -- new_interval parameter
            interval = max(interval * LAPSE_INTERVAL_MULTIPLIER, 1440)  # At least 1 day

            if len(INITIAL_RELEARN_INTERVALS) > 0:
                return SM2Result(phase=Phase.RELEARN, ease=ease, interval=INITIAL_RELEARN_INTERVALS[0], step=0)

            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval)
        elif choice == Choice.HARD:
            ease = max(1.3, card.ease * (1 - 0.15))
            interval = min(
                interval * 1.2,  # TODO: convert 1.2 to a variable -> hard_interval_multiplier
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
                (interval + rand_interval) * ease * EASY_BONUS,
                1440 * 36500 # 100 years
            )

            return SM2Result(phase=Phase.EXPONENTIAL, ease=ease, interval=interval)

    @staticmethod
    def _handle_relearn(card: Card, choice: Choice) -> SM2Result:
        step = card.step

        if len(INITIAL_RELEARN_INTERVALS) == 0 or card.step >= len(INITIAL_RELEARN_INTERVALS):
            interval = card.interval * card.ease
            return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=interval, ease=card.ease)

        if choice == Choice.AGAIN:
            return SM2Result(phase=Phase.RELEARN, step=0, interval=INITIAL_RELEARN_INTERVALS[0])
        elif choice == Choice.HARD:
            if step == 0 and len(INITIAL_RELEARN_INTERVALS) == 1:
                return SM2Result(phase=Phase.RELEARN, step=0, interval=int(INITIAL_RELEARN_INTERVALS[0] * 1.5))
            elif step == 0 and len(INITIAL_RELEARN_INTERVALS) > 1:
                return SM2Result(phase=Phase.RELEARN, step=0, interval=(INITIAL_RELEARN_INTERVALS[step] + INITIAL_RELEARN_INTERVALS[step+1]) / 2)

            return SM2Result(phase=Phase.RELEARN, step=0, interval=INITIAL_RELEARN_INTERVALS[step])
        elif choice == Choice.GOOD:
            if step + 1 == len(INITIAL_RELEARN_INTERVALS):
                return SM2Result(phase=Phase.EXPONENTIAL, step=None, interval=card.interval * card.ease)

            return SM2Result(phase=Phase.RELEARN, step=step + 1, interval=INITIAL_RELEARN_INTERVALS[step+1])
        elif choice == Choice.EASY:
            interval = min(
                card.interval * card.ease * EASY_BONUS,
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