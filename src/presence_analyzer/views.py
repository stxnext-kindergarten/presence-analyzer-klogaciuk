# -*- coding: utf-8 -*-
"""
Defines views.
"""
# pylint: disable=no-name-in-module,import-error

import calendar
import logging
import time

from flask import abort, redirect
from flask.ext.mako import exceptions, render_template
from lxml import etree

from presence_analyzer.main import app
from presence_analyzer.utils import (
    get_data,
    group_by_weekday,
    jsonify,
    mean,
    seconds_since_midnight,
)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view_v1():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v2/users', methods=['GET'])
@jsonify
def users_view_v2():
    """
    Users listing for dropdown.
    """
    # pylint: disable=no-member
    with open(app.config['USERS_XML_FILE'], 'r') as usersxmlfile:
        tree = etree.parse(usersxmlfile)
    url_base = "{}://{}".format(
        tree.find('server').findtext('protocol'),
        tree.find('server').findtext('host'),
    )
    return [
        {
            'user_id': elem.get('id'),
            'name': elem.findtext('name'),
            'avatar': '{}{}'.format(url_base, elem.findtext('avatar')),
        }
        for elem in tree.findall('./users/user')
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
        return 'NO_USER_DATA'

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
        return 'NO_USER_DATA'

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
        return 'NO_USER_DATA'

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
    """
    Returns rendered html files.
    """
    urls = {
        'presence_weekday': 'Presence weekday',
        'mean_time_weekday': 'Mean time weekday',
        'presence_start_end': 'Presence start end',
    }
    try:
        return render_template(template + '.html', urls=urls)
    except (exceptions.TopLevelLookupException, exceptions.SyntaxException):
        abort(404)
