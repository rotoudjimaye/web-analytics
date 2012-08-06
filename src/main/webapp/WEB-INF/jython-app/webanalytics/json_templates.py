# -*- coding: utf-8 -*-

import datetime
import math
from django.utils import timezone

from webanalytics.reporting import *
from webanalytics.json_transforms import  json_transform
import simplejson as json
from webanalytics.models import *
from django.db import connection, transaction

from datetime_utils import datetime2millis, millis2datetime, dtrange

PAGEVIEW_STATS_TEMPLATE = {
    "id":None,
    "name":None, 
    "adomain.account.id":None,
    "adomain.domain":None,
    "timestamp": None, 
    
    "history":  [
        {'$attr': "timestamp", 'label': "Unique Visitors",   "idx": 0,  'type': "datetime"},
        {'$attr': "visitors",  'label': "Unique Visitors", "idx": 1,  'type': "number", "$suffix": ""},     
        {'$attr': "pageviews", 'label': "Total Page Views", "idx": 2,  'type': "number", "$suffix": ""}, 
     
        {'$attr': "avg_visit_duration",      'label': "Avg Duration per Visitor", "idx": 3,  'type': "number", "$suffix": " secs"},
        {'$attr': "avg_pageviews_per_visit", 'label': "Avg Page Views per Visitor", "idx": 4,  'type': "number", "$suffix": ""},
        ],
    }

ENTRY_EXIT_PAGE_STATS_TEMPLATE = {    
    "items": {
        "pathname": None,
        "history":  [
            {'$attr': "timestamp", 'label': "time",   "idx": 0,  'type': "datetime"},
            {'$attr': "visitors",  'label': "Unique Visitors", "idx": 1,  'type': "number", "$suffix": ""},     
            {'$attr': "pageviews", 'label': "Total Page Views", "idx": 2,  'type': "number", "$suffix": ""}, 
            
            {'$attr': "percent_entry",      'label': "Avg Duration per Visitor", "idx": 3,  'type': "number", "$suffix": " %"},
            {'$attr': "percent_exit", 'label': "Avg Page Views per Visitor", "idx": 4,  'type': "number", "$suffix": " %"},
            ],
        }
    }
    

COUNTRY_STATS_TEMPLATE = {
    "items": {
        "code": None,
        "name": None,
        "history":  [
            {'$attr': "timestamp", 'label': "time",   "idx": 0,  'type': "datetime"},
            {'$attr': "visitors",  'label': "Top Countries - Unique Visitors", "idx": 1,  'type': "number", "$suffix": ""},     
            {'$attr': "pageviews", 'label': "Top Countries - Total Page Views", "idx": 2,  'type': "number", "$suffix": ""}, 
            {'$attr': "percent_visitors",  'label': "Top Countries - Percent Visitors", "idx": 1,  'type': "number", "$suffix": " %"},
            ],
        }
    }

CITY_STATS_TEMPLATE = {
    
    "items": {
        "name": None,
        "history":  [
            {'$attr': "timestamp", 'label': "time",   "idx": 0,  'type': "datetime"},
            {'$attr': "visitors",  'label': "Top Cities - Unique Visitors", "idx": 1,  'type': "number", "$suffix": ""},     
            {'$attr': "pageviews", 'label': "Top Cities - Total Page Views", "idx": 2,  'type': "number", "$suffix": ""}, 
            {'$attr': "percent_visitors",  'label': "Top Cities - Percent Visitors", "idx": 1,  'type': "number", "$suffix": " %"},
            ],
        }
    }

class Wrapper():
    def __init__(self, items, latest):
        self.items = items
        self.latest = latest

#
# simplejson handlers for datetime types et al.
#
def json_handler(obj):
    if isinstance(obj, datetime.datetime):
        return datetime2millis(obj)
    return str(obj)

#
# PAGEVIEW BASIC REPORTS
#
def get_start_end(latest, timedelta):
    end = timezone.now()
    start = millis2datetime(long(latest)) if latest else (end - timedelta)
    return start, end

def get_ten_minute_stats_history(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(hours=24))
    last_stat = get_domain_page_view_stats(adomain, start, end, VisitorPageviewTenMinuteStats)
    last_stat.history = list(VisitorPageviewTenMinuteStats.objects.filter(timestamp__gt=start, adomain=adomain).order_by("timestamp"))
    return json.dumps(json_transform(last_stat, PAGEVIEW_STATS_TEMPLATE, {'latest': end, 'live': live_pageview_stats(adomain)}), default=json_handler)

def get_hourly_stats_history(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=1))
    last_stat = get_domain_page_view_stats(adomain, start, end, VisitorPageviewTenMinuteStats)
    last_stat.history = list(VisitorPageviewHourlyStats.objects.filter(timestamp__gt=start, adomain=adomain).order_by("timestamp"))
    return json.dumps(json_transform(last_stat, PAGEVIEW_STATS_TEMPLATE, {'latest': end, 'live': live_pageview_stats(adomain)}), default=json_handler)

def get_daily_stats_history(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=30))
    last_stat = get_domain_page_view_stats(adomain, start, end, VisitorPageviewTenMinuteStats)
    last_stat.history = list(VisitorPageviewDailyStats.objects.filter(timestamp__gt=start, adomain=adomain).order_by("timestamp"))
    return json.dumps(json_transform(last_stat, PAGEVIEW_STATS_TEMPLATE, {'latest': end, 'live': live_pageview_stats(adomain)}), default=json_handler)

#
# TOP Cities
# 
class City():
    def __init__(self, name, history):
        self.name, self.history = name, history

def get_top_cities(adomain, start, end):
    cursor = connection.cursor()
    cursor.execute(" SELECT v.city, COUNT(v.id) FROM main_visitorsession v WHERE v.domain = %s "
                   " AND v.start >= %s AND v.start < %s GROUP BY v.city ORDER BY COUNT(v.id) DESC ", 
                   [adomain.domain, start, end])
    return [City(row[0], []) for row in cursor.fetchall()[0:3]]

def get_city_stats_hourly(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=1))
    cities = get_top_cities(adomain, start, end)
    for city in cities:
        for t in dtrange(start.replace(minute=0, second=0, microsecond=0), end, datetime.timedelta(hours=1)):
            city.history.extend(list(VisitorCityHourlyStats.objects.filter(adomain=adomain, timestamp=t, city=city)) or [VisitorCityHourlyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(cities, end), CITY_STATS_TEMPLATE), default=json_handler)

def get_city_stats_daily(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=7))
    cities = get_top_cities(adomain, start, end)
    for city in cities:
        for t in dtrange(start.replace(minute=0, second=0, microsecond=0), end, datetime.timedelta(days=1)):
            city.history.extend(list(VisitorCityDailyStats.objects.filter(adomain=adomain, timestamp=t, city=city)) or [VisitorCityDailyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(cities, end), CITY_STATS_TEMPLATE), default=json_handler)



#
# TOP COUNTRIES
#
def get_top_countries(adomain, start, end):
    cursor = connection.cursor()
    cursor.execute(" SELECT v.country_id, COUNT(v.id) FROM main_visitorsession v"
                   " WHERE v.domain = %s AND v.start >= %s AND v.start < %s AND v.country_id IS NOT NULL "
                   " GROUP BY v.country_id ORDER BY COUNT(v.id) DESC ", 
                   [adomain.domain, start, end])
    return [Country.objects.get(id=row[0]) for row in cursor.fetchall()[0:3]]

def get_country_stats_hourly(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=1))
    countries = get_top_countries(adomain, start, end)
    for country in countries:
        country.history = []
        for t in dtrange(start.replace(minute=0, second=0, microsecond=0), end, datetime.timedelta(hours=1)):
            country.history.extend(list(VisitorCountryHourlyStats.objects.filter(adomain=adomain, timestamp=t, country=country)) or [VisitorCountryHourlyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(countries, end), COUNTRY_STATS_TEMPLATE), default=json_handler)

def get_country_stats_daily(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=7))
    countries = get_top_countries(adomain, start, end)
    for country in countries:
        country.history = []
        for t in dtrange(start.replace(hour=0, minute=0, second=0, microsecond=0), end, datetime.timedelta(days=1)):
            country.history.extend(list(VisitorCountryDailyStats.objects.filter(adomain=adomain, timestamp=t, country=country)) or [VisitorCountryDailyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(countries, end), COUNTRY_STATS_TEMPLATE), default=json_handler)


#
# TOP ENTRY AND EXIT PAGES
#
class Page():
    def __init__(self, pathname, history):
        self.pathname, self.history = pathname, history

def get_top_entry_pages(adomain, start, end):
    cursor = connection.cursor()
    cursor.execute(" SELECT v.entry_page, COUNT(v.id) FROM main_visitorsession v"
                   " WHERE v.domain = %s AND v.start >= %s AND v.start < %s AND v.country_id IS NOT NULL "
                   " GROUP BY v.entry_page ORDER BY COUNT(v.id) DESC ", 
                   [adomain.domain, start, end])
    return [Page(row[0], []) for row in cursor.fetchall()[0:3]]

def get_top_exit_pages(adomain, start, end):
    cursor = connection.cursor()
    cursor.execute(" SELECT v.exit_page, COUNT(v.id) FROM main_visitorsession v"
                   " WHERE v.domain = %s AND v.start >= %s AND v.start < %s AND v.country_id IS NOT NULL "
                   " GROUP BY v.exit_page ORDER BY COUNT(v.id) DESC ", 
                   [adomain.domain, start, end])
    return [Page(row[0], []) for row in cursor.fetchall()[0:3]]

def get_top_entry_pages_stats_hourly(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=1))
    pages = get_top_entry_pages(adomain, start, end)
    for page in pages:
        page.history = []
        for t in dtrange(start.replace(minute=0, second=0, microsecond=0), end, datetime.timedelta(hours=1)):
            page.history.extend(list(DomainPageHourlyStats.objects.filter(adomain=adomain, timestamp=t, pathname=page.pathname)) or [DomainPageHourlyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(pages, end), ENTRY_EXIT_PAGE_STATS_TEMPLATE), default=json_handler)

def get_top_entry_pages_stats_daily(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=7))
    pages = get_top_entry_pages(adomain, start, end)
    for page in pages:
        page.history = []
        for t in dtrange(start.replace(hour=0, minute=0, second=0, microsecond=0), end, datetime.timedelta(days=1)):
            page.history.extend(list(DomainPageDailyStats.objects.filter(adomain=adomain, timestamp=t, pathname=page.pathname)) or [DomainPageHourlyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(pages, end), ENTRY_EXIT_PAGE_STATS_TEMPLATE), default=json_handler)

def get_top_entry_pages_stats_hourly(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=1))
    pages = get_top_exit_pages(adomain, start, end)
    for page in pages:
        page.history = []
        for t in dtrange(start.replace(minute=0, second=0, microsecond=0), end, datetime.timedelta(hours=1)):
            page.history.extend(list(DomainPageHourlyStats.objects.filter(adomain=adomain, timestamp=t, pathname=page.pathname)) or [DomainPageHourlyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(pages, end), ENTRY_EXIT_PAGE_STATS_TEMPLATE), default=json_handler)

def get_top_entry_pages_stats_daily(adomain, latest=None):
    start, end = get_start_end(latest, datetime.timedelta(days=7))
    pages = get_top_exit_pages(adomain, start, end)
    for page in pages:
        page.history = []
        for t in dtrange(start.replace(hour=0, minute=0, second=0, microsecond=0), end, datetime.timedelta(days=1)):
            page.history.extend(list(DomainPageDailyStats.objects.filter(adomain=adomain, timestamp=t, pathname=page.pathname)) or [DomainPageHourlyStats(timestamp=t)])
    return json.dumps(json_transform(Wrapper(pages, end), ENTRY_EXIT_PAGE_STATS_TEMPLATE), default=json_handler)

