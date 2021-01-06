import os
from datetime import datetime

from django.core.management.base import CommandError


def date_from_string(date_time_str: str) -> datetime:
    """example string to be parsed: 2020-12-29 17:09:00"""
    return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")


def date_to_string(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def check_is_file_exists(file: str) -> None:
    """Raise error if file does not exists"""
    if not os.path.isfile(file):
        raise CommandError('File "%s" does not exist' % file)
