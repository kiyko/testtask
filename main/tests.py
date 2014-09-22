import os
import yaml
import json

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
