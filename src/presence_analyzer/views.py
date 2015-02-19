# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, abort, render_template
import time

from presence_analyzer.main import app
from presence_analyzer.utils import(
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    seconds_since_midnight
)

from jinja2 import TemplateNotFound
from jinja2.exceptions import TemplateSyntaxError

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = {x: {'start': [], 'end': []} for x in range(7)}

    for day in data[user_id].keys():
        weekdays[day.weekday()]['start'].append(
            seconds_since_midnight(data[user_id][day]['start'])
        )
        weekdays[day.weekday()]['end'].append(
            seconds_since_midnight(data[user_id][day]['end'])
        )
    for day_idx in weekdays.keys():
        start_time_tuple = time.gmtime(mean(weekdays[day_idx]['start']))
        end_time_tuple = time.gmtime(mean(weekdays[day_idx]['end']))
        weekdays[day_idx]['start'] = [
            start_time_tuple.tm_hour,
            start_time_tuple.tm_min,
            start_time_tuple.tm_sec,
        ]

        weekdays[day_idx]['end'] = [
            end_time_tuple.tm_hour,
            end_time_tuple.tm_min,
            end_time_tuple.tm_sec,
        ]

    return weekdays


@app.route('/<template>')
def render_html(template):
    urls = {
        'presence_weekday': 'Presence weekday',
        'mean_time_weekday': 'Mean time weekday',
        'presence_start_end': 'Presence start end',
        }
    try:
        return render_template(template + '.html', urls=urls)
    except TemplateSyntaxError:
        abort(404)
    except TemplateNotFound:
        abort(404)
