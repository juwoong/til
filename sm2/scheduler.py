from datetime import datetime
import typing as t

from database import Database
from dto import Data, Card

class Scheduler:
    # 데이터 가져오고
    # 카드 생성하고
    # 데이터에 is_generated 업데이트하고
    # Card 객체 반환하기
    available_priorities: t.List[int] = [0, 1, 2]
    db: Database

    def __init__(self, db_name: str):
        self.db = Database(db_name)

    def _load_unused_data(self, limit: int) -> t.List[Data]:
        results = []

        for priority in self.available_priorities:
            query = f"SELECT * FROM datas WHERE is_generated = 0 AND priority = {priority} ORDER BY RANDOM() LIMIT {limit - len(results)};"
            results += self.db.fetch_all(query, Data)

            if len(results) >= limit:
                break

        return results
    
    def _create_new_card(self, data: Data) -> Card :
        card = Card(data_id=data.id)

        self.db.execute(card)
        last_id = self.db.cursor.lastrowid

        card.id = last_id

        return card

    def load_learning_cards(self, limit: int):
        """ only for stop during learning """
        pass

    def load_after_learning_cards(self, limit: int):
        pass

    def create_new_schedules(self, now: datetime):
        pass