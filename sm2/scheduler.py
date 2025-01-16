from datetime import datetime
import typing as t

from database import Database
from dto import Data, Card, Phase, Schedule, ScheduleStatus

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
    
    def _create_new_card(self, data: Data) -> Card:
        card = Card(data_id=data.id)

        card.id = self.db.insert(card)
        card.data = data
        return card
    
    def _load_exponential_cards(self, now) -> t.List[Card]:
        date_format = now.strftime('%Y-%m-%d %H:%M:%S')
        query = f"SELECT * FROM cards WHERE next_review <= '{date_format}' AND phase = {Phase.EXPONENTIAL.value};"
        cards = self.db.fetch_all(query, Card)

        for card in cards: 
            data = self.db.fetch_all(f"SELECT * FROM datas WHERE id = {card.data_id};", Data)[0]
            card.data = data

        return cards

    def _create_new_schedule(self, now: datetime) -> Schedule:
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        schedule = Schedule(date=start_date, status=ScheduleStatus.NOT_STARTED)
        schedule.id = self.db.insert(schedule)

        return schedule
    
    def _load_card_by_id(self, card_id: int) -> Card:
        query = f"SELECT * FROM cards WHERE id = {card_id};"
        card = self.db.fetch_all(query, Card)[0]

        data = self.db.fetch_all(f"SELECT * FROM datas WHERE id = {card.data_id};", Data)[0]
        card.data = data

        return card
    
    def _fill_schedule_instances(self, schedule: Schedule) -> Schedule: 
        schedule.created_cards = [self._load_card_by_id(card_id) for card_id in schedule.created]
        schedule.learning_cards = [self._load_card_by_id(card_id) for card_id in schedule.learning]
        schedule.reviewed_cards = [self._load_card_by_id(card_id) for card_id in schedule.reviewed]

        return schedule
        
    def get_schedule(self, now: datetime) -> Schedule: 
        # 현재 열려있는 스케줄이 있는지 확인
        schedules = self.db.fetch_all(f"SELECT * FROM schedules WHERE status IN ({ScheduleStatus.NOT_STARTED.value}, {ScheduleStatus.IN_PROGRESS.value}) ORDER BY status DESC;", Schedule)

        if schedules:  # 날짜랑 상관없이 가장 최근에 열린 스케줄을 반환
            return self._fill_schedule_instances(schedules[0])

        # 없으면 새로운 스케줄 생성
        schedule = self._create_new_schedule(now)

        # 데이터 가져오기
        new_datas = self._load_unused_data(10)

        # 카드 생성하기
        new_cards = [self._create_new_card(data) for data in new_datas]

        # 데이터에 is_generated 업데이트하기
        for data in new_datas:
            data.is_generated = True
            self.db.update(data)

        # 복습 카드 가져오기
        exponential_cards = self._load_exponential_cards(now)

        schedule.created = [card.id for card in new_cards]
        schedule.reviewed = [card.id for card in exponential_cards]

        self.db.update(schedule)

        schedule.created_cards = new_cards
        schedule.reviewed_cards = exponential_cards

        return schedule
