import time 
from datetime import datetime


def struct_time_to_datetime(struct_time: time.struct_time) -> datetime:
    return datetime(*struct_time[:6])
