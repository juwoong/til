import asyncpg
from config import Config
from datetime import datetime, timedelta


cfg = Config()


async def _get_db_connection():
    return await asyncpg.connect(
        host=cfg.DB_HOST,
        port=cfg.DB_PORT,
        database=cfg.DB_NAME,
        user=cfg.DB_USER,
        password=cfg.DB_PASSWORD,
    )


async def _get_query_result(query: str):
    conn = await _get_db_connection()

    result = []
    try:
        rows = await conn.fetch(query)

        result = [dict(row) for row in rows]
    finally:
        await conn.close()

    return result


async def get_articles_by_korean_date(dt: str): 
    date = datetime.strptime(dt, '%Y-%m-%d')

    start_date = date - timedelta(hours=9)
    end_date = start_date + timedelta(days=1)

    formatted_start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
    formatted_end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

    query = f"""
    SELECT title, original_content, summary, published_at, url FROM public.contents WHERE published_at >= '{formatted_start_date}' AND published_at < '{formatted_end_date}';
    """

    return await _get_query_result(query)

