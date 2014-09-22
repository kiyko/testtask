import json

from unittest import TestCase
from django.test import Client


class RequestTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_data(self):
        response = self.client.get('/data/users/')
        #
        self.assertEqual(response.status_code, 200)
        #
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content['id'], 'users')

    def test_create(self):
        response = self.client.post('/create/users/',
                                    {'name': 'UnitTest',
                                     'paycheck': 10,
                                     'date_joined': '2014-01-01'})
        #
        self.assertEqual(response.status_code, 200)
        #
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content['msg'], 'Model created')
        self.assertListEqual(content['values'][1:],
                             ['UnitTest', 10, '2014-01-01'])

    def test_update(self):
        def _first_row():
            response = self.client.get('/data/users/')
            #
            content = json.loads(response.content.decode("utf-8"))
            return content['values'][0]

        pk = _first_row()[0]
        #
        response = self.client.post('/update/users/{}/'.format(pk),
                                    {'date_joined': '2014-01-02'})
        #
        self.assertEqual(response.status_code, 200)
        #
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content['msg'], 'Model updated')
        self.assertEqual(content['pk'], pk)
        #
        date = _first_row()[3]
        self.assertEqual(date, '2014-01-02')
