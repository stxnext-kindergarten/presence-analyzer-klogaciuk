# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import logging
import time
import threading
from datetime import datetime
from functools import wraps
from json import dumps

from flask import Response

from presence_analyzer.main import app

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


CACHE = {}
TIMESTAMPS = {}


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def memorize(period):
    """
    Memorizing decorator. Returning cached data
    if its validity period is not expired.
    """

    def _decoration_wrapper(func):
        lock = threading.Lock()

        def _caching_wrapper(*args, **kwargs):
            cache_key = func.__name__
            now = time.time()
            if TIMESTAMPS.get(cache_key, now) > now:
                return CACHE[cache_key]
            with lock:
                if TIMESTAMPS.get(cache_key, now) > now:
                    return CACHE[cache_key]
                ret = func(*args, **kwargs)
                CACHE[cache_key] = ret
                TIMESTAMPS[cache_key] = now + period
                return ret
        return _caching_wrapper
    return _decoration_wrapper


@memorize(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time_base):
    """
    Calculates amount of seconds since midnight.
    """
    return time_base.hour * 3600 + time_base.minute * 60 + time_base.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
