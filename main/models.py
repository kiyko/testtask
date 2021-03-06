import os
import sys
import inspect
import yaml

from django.db import models


def setup_models(field_types):
    def _field(fld):
        if 'id' not in fld:
            raise Exception('Parameter `id` not found')
        #
        if 'type' not in fld:
            raise Exception('Parameter `type` not found')
        #
        tp = fld['type']
        if tp not in field_types:
            raise Exception('Type `{}` not supported'.format(tp))
        #
        opts = {}
        if 'title' in fld:
            opts.update({'verbose_name': fld['title']})
        #
        return {fld['id']: field_types[tp](**opts)}

    mod = sys.modules[__name__]  # current module
    #
    with open(os.path.join(os.path.dirname(__file__), 'models.yaml'), mode='r',
              encoding='utf-8') as schema_file:
        # Loads data schema
        schema = yaml.load(schema_file)
    # Creates models from data schema
    for (mdl_id, mdl) in schema.items():
        flds = {'__module__': __name__}
        #
        if 'title' in mdl:
            title = mdl['title']
            flds.update({'Meta': type('Meta', (object,),
                                      {'verbose_name': title,
                                       'verbose_name_plural': title})})
        #
        if 'fields' in mdl:
            # Adds order of fields into data schema
            mdl.update({'order': tuple(fld['id'] for fld in mdl['fields'])})
            # Adds fields into model
            for fld in mdl['fields']:
                flds.update(_field(fld))
        # Adds model into module
        setattr(mod, mdl_id, type(mdl_id, (models.Model,), flds))
    # Adds data schema into module
    setattr(mod, 'schema', schema)


def get_models():
    def _is_model(member):
        return (inspect.isclass(member) and issubclass(member, models.Model))

    return inspect.getmembers(sys.modules[__name__], _is_model)


def get_model(mdl_id):
    mod = sys.modules[__name__]  # current module
    #
    if not hasattr(mod, mdl_id):
        return None
    #
    return getattr(mod, mdl_id)


class _CharField(models.CharField):
    '''
    CharField wrapper for HTML-escaped strings with a maximum length of 255
    characters
    '''

    def __init__(self, **kwargs):
        super().__init__(max_length=255, **kwargs)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return value.replace('<', '&#60;').replace('>', '&#62;') \
                    .replace("'", '&#39;').replace('"', '&#34;')


setup_models(field_types={'char': _CharField,
                          'int': models.IntegerField,
                          'date': models.DateField})
