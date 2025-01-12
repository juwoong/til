import typing as t
import re

def parse_create_tables(sql) -> t.List[str]:
    lower_sql = sql.lower()
    pattern = re.compile(r"create table");

    results = []
    match = pattern.search(lower_sql)


    while match:
        next = pattern.search(lower_sql, match.end() + 1)
        next_index = next.start() if next else len(lower_sql)

        results.append(sql[match.start():next_index])
        match = next

    return results
