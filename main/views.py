import json
from collections import OrderedDict

from django.views.generic import TemplateView, View
from django.http import Http404, HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from main import models


class Index(TemplateView):
    '''
    Home page
    '''
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        # Context
        data = super().get_context_data(**kwargs)
        data['models'] = [{'id': mdl_id, 'title': mdl['title']}
                          for (mdl_id, mdl) in models.schema.items()]
        return data


class Data(View):
    '''
    Data in JSON format
    '''
    def get(self, request, *args, **kwargs):
        if 'mdl' not in self.kwargs:
            raise Http404()
        # Responds to the GET request
        return HttpResponse(self.get_data(mdl_id=self.kwargs['mdl']),
                            content_type='application/json; charset=utf-8')

    def get_data(self, mdl_id):
        if mdl_id not in models.schema:
            raise Http404()
        # Defines the struct of model
        content = models.schema[mdl_id].copy()
        content.update({'id': mdl_id})
        # Defines data of model
        mdl = models.get_model(mdl_id)  # class of the model
        data = serializers.serialize('python', mdl.objects.all())
        #
        order = OrderedDict((fld, '') for fld in content['order'])
        content.update({
            'values': [_ord_data(datum['pk'], datum['fields'], order)
                       for datum in data]
        })
        #
        return json.dumps(content, cls=DjangoJSONEncoder)


class Create(View):
    '''
    Data creator
    '''
    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        if 'mdl' in self.kwargs:
            mdl_id = self.kwargs['mdl']
            mdl = models.get_model(mdl_id)  # class of the model
            # Adds record
            vals = self.request.POST.dict()
            obj = mdl(**vals)
            obj.save()
            # Creates content
            content = {'msg': 'Model created'}
            datum = serializers.serialize('python',
                                          [mdl.objects.get(pk=obj.pk)])[0]
            order = OrderedDict((fld, '')
                                for fld in models.schema[mdl_id]['order'])
            content.update({
                'values': _ord_data(datum['pk'], datum['fields'], order)
            })
        else:
            content = {'msg': 'Missing some parameters'}
        # Responds to the POST request
        return HttpResponse(json.dumps(content, cls=DjangoJSONEncoder),
                            content_type='application/json; charset=utf-8')


class Update(View):
    '''
    Data updater
    '''
    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        if ('mdl' in self.kwargs) and ('pk' in self.kwargs):
            mdl = models.get_model(self.kwargs['mdl'])  # class of the model
            # Updates fields
            obj = mdl.objects.get(pk=self.kwargs['pk'])
            for (fld, val) in self.request.POST.items():
                if hasattr(obj, fld):
                    setattr(obj, fld, val)
            obj.save()
            #
            content = {'msg': 'Model updated', 'pk': obj.pk}
        else:
            content = {'msg': 'Missing some parameters'}
        # Responds to the POST request
        return HttpResponse(json.dumps(content),
                            content_type='application/json; charset=utf-8')


def _ord_data(pk, vals, order):
    for (fld, val) in vals.items():
        order[fld] = val
    return [pk] + list(order.values())
