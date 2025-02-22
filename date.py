import re
from datetime import datetime, time, timedelta

DATE_STR_FULL_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_STR_BASIC_FORMAT = '%Y-%m-%d'

DATE_FULL_PATTERN = r'[0-9]{4}\-[0-9]{2}-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2}'

def is_date_str_supported(s_date: str, pattern=DATE_FULL_PATTERN) -> bool:

    if re.match(pattern, s_date, re.IGNORECASE):
        return True
    else:
        return False

def to_date(s_date: str, s_format: str = DATE_STR_FULL_FORMAT) -> datetime:
    return datetime.strptime(s_date, s_format)

def to_day_start(_date: datetime) -> datetime:
    return datetime(_date.year, _date.month, _date.day)

def to_day_end(_date: datetime) -> datetime:
    return datetime(_date.year, _date.month, _date.day, time.max.hour, time.max.minute, time.max.second)

def to_str(_date: datetime, s_format=DATE_STR_FULL_FORMAT) -> str:
    return _date.strftime(s_format)

def days_ago(count: int, _date: datetime = datetime.now()) -> datetime:
    return _date - timedelta(days=count)

def minutes_ago(count: int, _date: datetime = datetime.now()) -> datetime:
    return _date - timedelta(minutes=count)

def seconds_ago(count: int, _date: datetime = datetime.now()) -> datetime:
    return _date - timedelta(seconds=count)

def build_time_frame(s_from, s_to = None, expand=False, close_time_frame=True, format_values = False, s_format=DATE_STR_FULL_FORMAT) -> dict:
    _time_frame = {}

    if isinstance(s_from, datetime):
        _date_from = s_from
    else:
        _date_from = to_date(s_from, s_format=s_format)

    _date_day_start = to_day_start(_date_from)

    _time_frame['date'] = _date_from

    if close_time_frame or s_to is not None:
        if s_to is not None:
            if isinstance(s_to, datetime):
                _date_end_time = s_to
            else:
                _date_end_time = to_date(s_to, s_format=s_format)
        else:
            _date_end_time = to_day_end(_date_from)

        if expand:
            _time_frame.update({
                'from': _date_day_start,
                'to': _date_end_time,
            })
        else:
            _time_frame.update({
                'from': _date_from,
                'to': _date_end_time,
            })
    else:
        if expand:
            _time_frame.update({
                'from': _date_day_start,
                'to': None,
            })
        else:
            _time_frame.update({
                'from': _date_from,
                'to': None,
            })

    if format_values:
        for key in list(_time_frame.keys()):
            _time_frame[key] = to_str(_time_frame[key], s_format=s_format)

    return _time_frame


TestMode = True
if TestMode:
    print(build_time_frame('2025-02-07T12:22:02'))
    print(build_time_frame('2025-02-07T12:22:02', expand=True))
    print(build_time_frame('2025-02-07T12:22:02', expand=True, close_time_frame=False))
    print(build_time_frame('2025-02-07T12:22:02', expand=False, close_time_frame=False))
    print(build_time_frame('2025-02-07', expand=True, s_format=DATE_STR_BASIC_FORMAT))
    print(build_time_frame('2025-02-07', expand=True, close_time_frame=False, s_format=DATE_STR_BASIC_FORMAT))
    print(build_time_frame('2025-02-07', expand=True, close_time_frame=False, s_format=DATE_STR_BASIC_FORMAT))
    print(build_time_frame(datetime.now(), expand=True, close_time_frame=False))
    print(build_time_frame(datetime.now(), expand=False, close_time_frame=False))
    print(build_time_frame(datetime.now(), expand=False, close_time_frame=True))
    print(build_time_frame(datetime.now(), expand=True, close_time_frame=True))
    print(build_time_frame(datetime.now() - timedelta(days=1), s_to=datetime.now(), expand=False, close_time_frame=True))
    print(build_time_frame(datetime.now() - timedelta(days=1), s_to=datetime.now(), expand=False, close_time_frame=True,
                         format_values=True))