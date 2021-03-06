# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import datetime
import json
import os.path
import unittest
from collections import defaultdict

from presence_analyzer import main, utils

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)
USERS_TEST_XML_FILE = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'users_test.xml'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update(
            {
                'DATA_CSV': TEST_DATA_CSV,
                'USERS_XML_FILE': USERS_TEST_XML_FILE,
            }
        )
        self.client = main.app.test_client()
        utils.TIMESTAMPS['get_data'] = 0

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday')

    def test_api_users_v1(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {'user_id': 10, 'name': 'User 10'})

    def test_api_users_v2(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v2/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

        expected_data = [
            {
                'user_id': '26',
                'name': 'Andrzej S.',
                'avatar': 'https://intranet.stxnext.pl/api/images/users/26',
            },
            {
                'user_id': '165',
                'name': 'Anna D.',
                'avatar': 'https://intranet.stxnext.pl/api/images/users/165',
            },
        ]
        self.assertListEqual(json.loads(resp.data), expected_data)

    def test_mean_time_weekday_view(self):
        """
        Test correctness of presenting data of mean presence
        time of given user grouped by weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)

        expected_res = [
            ["Mon", 0],
            ["Tue", 30047.0],
            ["Wed", 24465.0],
            ["Thu", 23705.0],
            ["Fri", 0],
            ["Sat", 0],
            ["Sun", 0],
        ]
        self.assertEqual(expected_res, data)

        resp = self.client.get('/api/v1/mean_time_weekday/1000')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), "NO_USER_DATA")

    def test_presence_weekday_view(self):
        """
        Test correctness of presenting data of presence by weekday.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)

        expected_res = [
            ["Weekday", "Presence (s)"],
            ["Mon", 0],
            ["Tue", 30047],
            ["Wed", 24465],
            ["Thu", 23705],
            ["Fri", 0],
            ["Sat", 0],
            ["Sun", 0],
        ]
        self.assertEqual(expected_res, data)

        resp = self.client.get('/api/v1/presence_weekday/1000')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), "NO_USER_DATA")

    def test_presence_start_end(self):
        """
        Test if function has returned correct values of user average
        working start time and user average working end time and.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertDictEqual(
            {
                '0': {
                    'start': [0, 0, 0],
                    'end': [0, 0, 0],
                },
                '1': {
                    'start': [9, 39, 5],
                    'end': [17, 59, 52],
                },
                '2': {
                    'start': [9, 19, 52],
                    'end': [16, 7, 37],
                },
                '3': {
                    'start': [10, 48, 46],
                    'end': [17, 23, 51],
                },
                '4': {
                    'start': [0, 0, 0],
                    'end': [0, 0, 0],
                },
                '5': {
                    'end': [0, 0, 0],
                    'start': [0, 0, 0],
                },
                '6': {
                    'end': [0, 0, 0],
                    'start': [0, 0, 0],
                },
            },
            data,
        )
        resp = self.client.get('/api/v1/presence_start_end/1000')
        self.assertEqual(json.loads(resp.data), 'NO_USER_DATA')
        self.assertEqual(resp.status_code, 200)

    def test_standard_deviation(self):
        """
        Test if function has returned correct standard deviation
        value of starting and ending work time.
        """
        resp = self.client.get('/api/v1/standard_deviation/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        expected_data = {
            'start_variation': [[9, 39, 5], [9, 39, 5]],
            'end_variation': [[17, 59, 52], [17, 59, 52]],
        }
        self.assertDictEqual(expected_data, json.loads(resp.data)['1'])

        resp = self.client.get('/api/v1/presence_start_end/1000')
        self.assertEqual(json.loads(resp.data), 'NO_USER_DATA')
        self.assertEqual(resp.status_code, 200)

    def test_render_html(self):
        """
        Test if function operate template rendering correctly.
        """
        resp = self.client.get('/presence_weekday')
        self.assertNotEqual(
            resp.data.find('Presence by weekday'),
            -1,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'text/html; charset=utf-8')

        resp = self.client.get('/presence_weekday_that_not_exists')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/template_with_errors')
        self.assertEqual(resp.status_code, 404)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        utils.TIMESTAMPS['get_data'] = 0
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_jsonify(self):
        """
        Test if function create a response result in JSON representation.
        """
        @utils.jsonify
        def return_dict():
            """
            Simple function returning dictionary for further tests.
            """
            return {1: 1, 2: 2}
        res = return_dict()
        self.assertEqual({'1': 1, '2': 2}, json.loads(res.data))

    def test_group_by_weekday(self):
        """
        Test if function groups presence entries by weekday.
        """
        example_date = {
            datetime.date(2013, 9, 10): {
                'start': datetime.time(9, 39, 5),
                'end': datetime.time(17, 59, 52),
            },
            datetime.date(2013, 9, 12): {
                'start': datetime.time(10, 48, 46),
                'end': datetime.time(17, 23, 51),
            },
            datetime.date(2013, 9, 11): {
                'start': datetime.time(9, 19, 52),
                'end': datetime.time(16, 7, 37),
            },
        }
        tested_res = utils.group_by_weekday(example_date)
        self.assertListEqual(
            [
                [],
                [30047],
                [24465],
                [23705],
                [],
                [],
                [],
            ],
            tested_res,
        )

    def test_seconds_since_midnight(self):
        """
        Test if function correctly calculate amount
        of seconds since midnight.
        """
        res = utils.seconds_since_midnight(datetime.time(22, 33, 11))
        self.assertEqual(81191, res)

    def test_interval(self):
        """
        Test if interval between two datetime.time objects is correct.
        """
        tested_interval = utils.interval(
            datetime.time(11, 22, 33),
            datetime.time(8, 11, 31)
        )
        self.assertEqual(-11462, tested_interval)

    def test_mean(self):
        """
        Test if arythmetic mean returned by funcion is correct.
        """
        self.assertEqual(0, utils.mean([]))
        self.assertEqual(2., utils.mean([1, 2, 3]))
        self.assertEqual(-2., utils.mean([-1, -2, -3]))
        self.assertEqual(2., utils.mean([1., 2., 3.]))

    def test_memorize(self):
        """
        Test caching of get_data method.
        """
        expected_data = {
            datetime.date(2013, 9, 10): {
                'start': datetime.time(9, 39, 5),
                'end': datetime.time(17, 59, 52),
            },
            datetime.date(2013, 9, 12): {
                'start': datetime.time(10, 48, 46),
                'end': datetime.time(17, 23, 51),
            },
            datetime.date(2013, 9, 11): {
                'start': datetime.time(9, 19, 52),
                'end': datetime.time(16, 7, 37),
            },
        }
        self.assertDictEqual(expected_data, utils.get_data()[10])
        utils.CACHE = {'get_data': {10: 'rubbish'}}
        self.assertNotEqual(expected_data, utils.get_data()[10])
        utils.TIMESTAMPS['get_data'] = 0
        self.assertDictEqual(expected_data, utils.get_data()[10])

    def test_mean_start_end_for_sv(self):
        """
        Test if function correctly counts mean time of
        starting and ending work time.
        """
        expected_data = {
            'start': 34745.0,
            'data_examples_num': 1,
            'end': 64792.0
        }
        self.assertDictEqual(
            expected_data,
            utils.get_mean_start_end(
                utils.get_data()[10]
            )[1],
        )

    def test_variation_start_end(self):
        """
        Test if function correctly counts variation from
        given data.
        """
        data = utils.get_data()
        day_start_end = {}
        for day_idx in range(7):
            day_start_end[day_idx] = defaultdict(lambda: 0)

        expected_data = {
            'end_variation': 2247001.0,
            'start_variation': 2292196.0,
        }
        weekdays = utils.get_mean_start_end(
            data[11]
        )
        day_start_end = utils.variation_for_day_start_end(
            day_start_end,
            data[11],
            weekdays,
        )
        self.assertDictEqual(day_start_end[3], expected_data)

    def t_standard_deviation_from_data(self):
        """
        Test if function retuns standard deviation
        from given variations.
        """
        data = utils.get_data()
        day_start_end = {}
        for day_idx in range(7):
            day_start_end[day_idx] = defaultdict(lambda: 0)
        weekdays = utils.get_mean_start_end(
            data[11]
        )
        day_start_end = utils.variation_for_day_start_end(
            day_start_end,
            data[11],
            weekdays,
        )
        expected_data = {
            'end_variation': [[15, 51, 27], [16, 41, 25]],
            'start_variation': [[9, 28, 8], [10, 18, 36]],
        }
        self.assertEqual(
            expected_data,
            utils.standard_deviation_from_data(
                day_start_end,
                weekdays)[3],
        )

    def test_equation_for_day(self):
        """
        Test if function properly counts particural
        part of variance equation.
        """
        self.assertAlmostEqual(
            22739.259661982247, utils.equation_for_day(
                datetime.time(8, 54, 29),
                30553.52475247525, 101
            )
        )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
