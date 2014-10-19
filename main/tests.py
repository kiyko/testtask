import os
import yaml
import json
import random

from datetime import date
from unittest import TestCase

from django.test import Client

from main import models


class ModelTest(TestCase):
    def setUp(self):
        self.schema = {}
        with open(os.path.join(os.path.dirname(__file__), 'models.yaml'),
                  mode='r', encoding='utf-8') as schema_file:
            # Loads data schema
            self.schema = yaml.load(schema_file)

    def test_ids(self):
        for (mdl_id, mdl) in self.schema.items():
            cls = models.get_model(mdl_id)
            self.assertNotEqual(cls, None)

    def test_fields(self):
        types = {'char': 'CharField',
                 'int': 'IntegerField',
                 'date': 'DateField'}
        #
        for (mdl_id, mdl) in self.schema.items():
            cls = models.get_model(mdl_id)
            names = cls._meta.get_all_field_names()
            #
            for fld in mdl['fields']:
                fld_id = fld['id']
                self.assertIn(fld_id, names)
                #
                fld_type = fld['type']
                fld_cls = cls._meta.get_field(fld_id)
                self.assertEqual(fld_cls.__class__.__name__, types[fld_type])


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
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['id'], 'users')

    def test_create(self):
        dt = self._rand_date()
        #
        response = self.client.post('/create/users/', {'name': 'UnitTest',
                                                       'paycheck': 10,
                                                       'date_joined': dt})
        #
        self.assertEqual(response.status_code, 200)
        #
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['msg'], 'Model created')
        self.assertListEqual(content['values'][1:], ['UnitTest', 10, dt])

    def test_update(self):
        pk = self._first_row()[0]
        dt = self._rand_date()
        #
        response = self.client.post('/update/users/{}/'.format(pk),
                                    {'date_joined': dt})
        #
        self.assertEqual(response.status_code, 200)
        #
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['msg'], 'Model updated')
        self.assertEqual(content['pk'], pk)
        #
        date = self._first_row()[3]
        self.assertEqual(date, dt)

    def _first_row(self):
        '''
        Returns data of a first row as list:
        [<pk>, <value of field 0>, <value of field 1>, ...]
        '''
        response = self.client.get('/data/users/')
        #
        content = json.loads(response.content.decode('utf-8'))
        return content['values'][0]

    def _rand_date(self):
        '''
        Returns random date as string: "YYYY-MM-DD"
        '''
        year = random.choice(range(1, 9999))
        month = random.choice(range(1, 12))
        day = random.choice(range(1, 28))
        #
        return date(year, month, day).isoformat()
