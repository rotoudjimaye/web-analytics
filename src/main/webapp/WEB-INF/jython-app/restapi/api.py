#-*- coding: utf-8 -*-


from tastypie.resources import ModelResource
from restapi.models import Entry

class EntryResource(ModelResource):
    class Meta:
        queryset = Entry.objects.all()
        resource_name = 'entry'

