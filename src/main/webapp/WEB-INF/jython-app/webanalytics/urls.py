# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^$', 'webanalytics.views.home'),
    
    url(r'^webanalytics.gif', 'webanalytics.views.hit'),

    url(r'^about-webanalytics/', 'webanalytics.views.app_about'),

    url(r'^analytics/home/', 'webanalytics.views.account_home'),
    
    url(r'^snippets/basic-dashboard/', 'webanalytics.views.snippet_basic_dashboard'),
    url(r'^snippets/entry-exit-pages-dashboard/', 'webanalytics.views.snippet_entry_exit_dashboard'),
    url(r'^snippets/geolocation-dashboard/', 'webanalytics.views.snippet_geolocation_dashboard'),

    url(r'^pageview/(\w+)/', 'webanalytics.views.reporting_pageview'),
    url(r'^top-cities/(\w+)/', 'webanalytics.views.reporting_top_cities'),
    url(r'^top-countries/(\w+)/', 'webanalytics.views.reporting_top_countries'),
    url(r'^top-entry-pages/(\w+)/', 'webanalytics.views.reporting_top_entry_pages'),
    url(r'^top-exit-pages/(\w+)/', 'webanalytics.views.reporting_top_exit_pages'),
    url(r'^download-csv/(\w+)/(\w+)/', 'webanalytics.views.download_csv')
)