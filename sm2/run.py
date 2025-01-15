from scheduler import Scheduler

scheduler = Scheduler('content.db')

result = scheduler.load_unused_data(10)

print(result)

# card = Card(
#     data_id=2,
#     phase=Phase.NEW,
#     last_review=datetime.now(),
#     next_review=datetime.now(),
# )

# db.insert(card)

# card = SM2.create_initial_card('test', 'test')

# print(card)

# def return_choice(input_choice) -> Choice:
#     return Choice(input_choice - 1)

# sm2 = SM2()
# expect = sm2.expected_interval(card)

# while True:
#     print(" | ".join([f"{i + 1}: {c.name} ({expect[i]})" for i, c in enumerate(Choice)]))
#     while True:
#         choice = int(input("Enter choice: "))

#         if not (1 <= choice <= 4):
#             print("Invalid choice. Please enter a number between 1 and 4.")
#             continue
#         break

#     result = sm2.get_next_card(card, return_choice(choice))
#     print(result, "\n")

#     card.phase = result.phase
#     card.step = result.step if result.step is not None else card.step
#     card.ease = result.ease if result.ease is not None else card.ease
#     card.interval = result.interval if result.interval is not None else card.interval
#     card.leech = result.leech if result.leech is not None else card.leech

#     expect = sm2.expected_interval(card)

