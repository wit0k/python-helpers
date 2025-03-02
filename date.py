import re
from datetime import datetime, time, timedelta

DATE_STR_FULL_FORMAT = '%Y-%m-%dT%H:%M:%S'
DATE_STR_BASIC_FORMAT = '%Y-%m-%d'

DATE_FULL_PATTERN = r'[0-9]{4}\-[0-9]{2}-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2}'
DATE_BASIC_PATTERN = r'[0-9]{4}\-[0-9]{2}-[0-9]{2}'

def is_date_str_supported(s_date: str, pattern=DATE_FULL_PATTERN) -> bool:

    if re.fullmatch(pattern, s_date, re.IGNORECASE):
        return True
    else:
        return False

def to_date(s_date: str, s_format: str = None) -> datetime:

    builtin_formats = [DATE_STR_BASIC_FORMAT, DATE_STR_FULL_FORMAT]
    if s_format is None: s_format = DATE_STR_BASIC_FORMAT
    if s_format not in builtin_formats: builtin_formats.insert(0, s_format)

    for _format in builtin_formats:
        try:
            return datetime.strptime(s_date, _format)
        except Exception as msg:
            print(s_date, msg)

    raise Exception('Unsupported s_date format! -> Supported formats: %s' % s_date)

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

def build_time_frame(s_from, s_to=None, use_day_start=False, include_end_time=True, format_values=False, s_format=DATE_STR_FULL_FORMAT) -> dict:
    """
        s_from: The starting point of the time frame. It can be a datetime object or a string.
        s_to: The ending point of the time frame. It is optional and can be a datetime object or a string.
        expand: A boolean flag that determines whether the time frame should start from the beginning of the day (True) or from the exact time specified by s_from (False).
        end_time_frame: A boolean flag that determines whether the time frame should have an end time (True) or not (False).
        format_values: A boolean flag that determines whether the dates should be formatted as strings (True) or kept as datetime objects (False).
        s_format: The format to use for formatting the dates if format_values is True.
    """
    _time_frame = {}

    if isinstance(s_from, datetime):
        _date_from = s_from
    else:
        _date_from = to_date(s_from, s_format=s_format)

    _date_day_start = to_day_start(_date_from)

    _time_frame['date'] = _date_from

    if include_end_time or s_to is not None:
        if s_to is not None:
            if isinstance(s_to, datetime):
                _date_end_time = s_to
            else:
                _date_end_time = to_date(s_to, s_format=s_format)
        else:
            _date_end_time = to_day_end(_date_from)

        if use_day_start:
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
        if use_day_start:
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
            if _time_frame[key] is None: continue
            _time_frame[key] = to_str(_time_frame[key], s_format=s_format)

    return _time_frame


TestMode = False
if TestMode:
    print(build_time_frame('2025-02-07T12:22:02'))
    print(build_time_frame('2025-02-07T12:22:02', use_day_start=True))
    print(build_time_frame('2025-02-07T12:22:02', use_day_start=True, include_end_time=False))
    print(build_time_frame('2025-02-07T12:22:02', use_day_start=False, include_end_time=False))
    print(build_time_frame('2025-02-07', use_day_start=True, s_format=DATE_STR_BASIC_FORMAT))
    print(build_time_frame('2025-02-07', use_day_start=True, include_end_time=False, s_format=DATE_STR_BASIC_FORMAT))
    print(build_time_frame('2025-02-07', use_day_start=True, include_end_time=False, s_format=DATE_STR_BASIC_FORMAT))
    print(build_time_frame(datetime.now(), use_day_start=True, include_end_time=False))
    print(build_time_frame(datetime.now(), use_day_start=False, include_end_time=False))
    print(build_time_frame(datetime.now(), use_day_start=False, include_end_time=True))
    print(build_time_frame(datetime.now(), use_day_start=True, include_end_time=True))
    print(build_time_frame(datetime.now() - timedelta(days=1), s_to=datetime.now(), use_day_start=False, include_end_time=True))
    print(build_time_frame(datetime.now() - timedelta(days=1), s_to=datetime.now(), use_day_start=False, include_end_time=True, format_values=True))
