-- card_data 테이블 더미 데이터
INSERT INTO datas (question, description, priority, is_generated) VALUES
('What is the capital of France?', 'Identify the capital city of France.', 0, 0),
('Solve for x: 2x + 3 = 7', 'Basic algebra problem to solve for x.', 0, 0),
('Who painted the Mona Lisa?', 'Name the artist of the famous painting.', 0, 0),
('What is the chemical symbol for Gold?', 'Recall the periodic table symbol for Gold.', 0, 0),
('Define photosynthesis.', 'Explain the process plants use to make food.', 1, 0),
('When did World War II end?', 'Provide the year World War II ended.', 1, 0),
('What is the powerhouse of the cell?', 'Identify the organelle responsible for energy.', 1, 0),
('Name the largest planet in our solar system.', 'Recall the largest planet.', 1, 0),
('Translate "Hello" to Spanish.', 'Provide the Spanish translation for "Hello".', 2, 0),
('What is Newtons second law?', 'State Newtons second law of motion.', 2, 0);

-- cards 테이블 더미 데이터 (card_data와 연결)
INSERT INTO cards (dataset_id, phase, interval, ease, leech, last_review, next_review) VALUES
(1, 1, 1, 2.5, 0, '2024-01-10 08:00:00', '2024-01-11 08:00:00'),
(2, 2, 3, 2.3, 0, '2024-01-09 09:00:00', '2024-01-12 09:00:00'),
(3, 1, 2, 2.7, 0, '2024-01-10 10:00:00', '2024-01-12 10:00:00'),
(4, 3, 5, 2.1, 1, '2024-01-07 11:00:00', '2024-01-12 11:00:00'),
(5, 1, 1, 2.6, 0, '2024-01-10 12:00:00', '2024-01-11 12:00:00'),
(6, 2, 4, 2.4, 0, '2024-01-08 13:00:00', '2024-01-12 13:00:00'),
(7, 1, 2, 2.8, 0, '2024-01-10 14:00:00', '2024-01-12 14:00:00'),
(8, 3, 6, 2.0, 1, '2024-01-06 15:00:00', '2024-01-12 15:00:00'),
(9, 1, 1, 2.9, 0, '2024-01-10 16:00:00', '2024-01-11 16:00:00'),
(10, 2, 3, 2.5, 0, '2024-01-09 17:00:00', '2024-01-12 17:00:00');