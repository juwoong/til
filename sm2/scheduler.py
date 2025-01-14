from datetime import datetime

class Scheduler:


    def load_new_cards(self, limit: int):
        pass

    def load_learning_cards(self, limit: int):
        """ only for stop during learning """
        pass

    def load_after_learning_cards(self, limit: int):
        pass

    def create_new_schedules(self, now: datetime):
        pass