from enum import Enum
import random

from const import EASY_BONUS, FIRST_EXPONENTIAL_INTERVAL, INITIAL_INTERVALS, INITIAL_RELEARN_INTERVALS, LAPSE_INTERVAL_MULTIPLIER


class Choice(int, Enum):
    AGAIN = 0
    HARD = 1
    GOOD = 2
    EASY = 3

class Phase(int, Enum): 
    LEARNING = 0
    EXPONENTIAL = 1
    RELEARN = 2


class SM2:
    def get_new_card(self):
        return INITIAL_INTERVALS
    
    def _handle_learning(self, card, choice):
        """
        return the next step and interval for the card
        """
        step = card.get('step', 0)

        if choice == Choice.AGAIN:
            return Phase.LEARNING, 0, INITIAL_INTERVALS[0]
        elif choice == Choice.HARD:
            return Phase.LEARNING, step, INITIAL_INTERVALS[step+1] / 2
        elif choice == Choice.GOOD:
            return Phase.LEARNING, step + 1, INITIAL_INTERVALS[step+1]
        elif choice == Choice.EASY:
            return Phase.EXPONENTIAL, 0, INITIAL_INTERVALS[-1] + FIRST_EXPONENTIAL_INTERVAL

    def _handle_exponential(self, card, choice):
        ease = card.get('ease', 2.5)
        interval = card.get('interval', 0)
        rand_interval = random.randrange(0, 1441)

        if choice == Choice.AGAIN:
            return Phase.RELEARN, ease - 0.2, interval * LAPSE_INTERVAL_MULTIPLIER
        elif choice == Choice.HARD:
            return Phase.EXPONENTIAL, ease - 0.15, interval * 1.2
        elif choice == Choice.GOOD:
            return Phase.EXPONENTIAL, ease, (interval + rand_interval) * ease
        elif choice == Choice.EASY:
            return Phase.EXPONENTIAL, ease + 0.15, (interval + rand_interval) * (ease * EASY_BONUS)


    def _handle_relearn(self, card, choice):
        step = card.get('step', 0)

        if choice == Choice.AGAIN:
            return Phase.RELEARN, 0, INITIAL_RELEARN_INTERVALS[0]
        elif choice == Choice.HARD:
            return Phase.RELEARN, step, INITIAL_RELEARN_INTERVALS[step+1] / 2
        elif choice == Choice.GOOD:
            return Phase.RELEARN, step + 1, INITIAL_RELEARN_INTERVALS[step+1]
        elif choice == Choice.EASY:
            return Phase.EXPONENTIAL, 0, INITIAL_RELEARN_INTERVALS[-1] + FIRST_EXPONENTIAL_INTERVAL
    
    def get_next_card(self, card, choice):
        phase = card.get('phase', Phase.LEARNING)

        if phase == Phase.LEARNING:
            return self._handle_learning(card, choice)
        elif phase == Phase.EXPONENTIAL:
            return self._handle_exponential(card, choice)
        elif phase == Phase.RELEARN:
            return self._handle_relearn(card, choice)