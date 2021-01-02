from datetime import datetime


def date_from_string(date_time_str: str) -> datetime:
    """example string to be parsed: 2020-12-29 17:09:00"""
    return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
