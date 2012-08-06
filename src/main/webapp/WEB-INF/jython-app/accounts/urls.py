# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login/', 'accounts.views.login'),
    url(r'^login2/', 'accounts.views.login'),
    url(r'^logout/', 'accounts.views.logout'),
)