# -*- coding: utf-8 -*-
"""
Reporting functions
"""

from models import *
import datetime
from django.utils import timezone

#
#
def get_ten_min_iterval(timestamp):
    end = timestamp.replace(second=0, microsecond=0)
    start = end - datetime.timedelta(minutes=10)
    return start, end

def get_hourly_iterval(timestamp):
    end = timestamp.replace(minute=0, second=0, microsecond=0)
    start = end - datetime.timedelta(hours=1)
    return start, end

def get_daily_iterval(timestamp):
    end = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - datetime.timedelta(days=1)
    return start, end
#
#
def get_domain_page_view_stats(adomain, start, end=None, Type=None):
    if end is None: end = timezone.now()
    page_views = list(PageView.objects.filter(adomain=adomain, timestamp__gte=start, timestamp__lt=end, visitor_session__end__isnull=False))
    visitor_sessions = set([p.visitor_session for p in page_views])
    if page_views:
        visitors = len(visitor_sessions)
        pageviews = len(page_views)
        total_duration = sum([vs.duration for vs in visitor_sessions])
        stat = dict(adomain=adomain, visitors=visitors, pageviews=pageviews,
                    avg_visit_duration=round(int(total_duration / visitors)),
                    avg_pageviews_per_visit=round((pageviews / visitors)),
                    timestamp=start)
    else:
        stat = dict(adomain=adomain, visitors=0, pageviews=0, avg_visit_duration=0, avg_pageviews_per_visit=0, timestamp=start)
    return stat if Type is None else Type(**stat)
    
def compute_minute_pageview_stats(timestamp):
    """ Computes PageView Stats for 10 minute time intervals """
    start, end = get_ten_min_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        page_views = list(PageView.objects.filter(adomain=adomain, timestamp__gte=start, timestamp__lt=end, visitor_session__end__isnull=False))
        visitor_sessions = set([p.visitor_session for p in page_views])
        VisitorPageviewTenMinuteStats(**get_domain_page_view_stats(adomain, start, end)).save()
    return start, end

def compute_hourly_pageview_stats(timestamp):
    """ Computes PageView Stats for 10 minute time intervals """
    start, end = get_hourly_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        page_views = list(PageView.objects.filter(adomain=adomain, timestamp__gte=start, timestamp__lt=end, visitor_session__end__isnull=False))
        visitor_sessions = set([p.visitor_session for p in page_views])
        VisitorPageviewHourlyStats(**get_domain_page_view_stats(adomain, start, end)).save()
    return start, end

def compute_daily_pageview_stats(timestamp):
    """ Computes PageView Stats for 10 minute time intervals """
    start, end = get_daily_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        page_views = list(PageView.objects.filter(adomain=adomain, timestamp__gte=start, timestamp__lt=end, visitor_session__end__isnull=False))
        visitor_sessions = set([p.visitor_session for p in page_views])
        VisitorPageviewDailyStats(**get_domain_page_view_stats(adomain, start, end)).save()
    return start, end

#
# Page Entry and Exit Analysis
#
def get_all_visited_pages(adomain, start, end):
    page_views = list(PageView.objects.filter(adomain=adomain, timestamp__gte=start, timestamp__lt=end, visitor_session__end__isnull=False))
    visited_pages = set([p.browser_pathname for p in page_views])
    visitor_sessions = set([p.visitor_session for p in page_views])
    visitors = len(visitor_sessions)
    result = []
    for path in visited_pages:
        result.append(dict(adomain=adomain, timestamp=start, pathname=path, 
                    pageviews=len([p for p in page_views if p.browser_pathname==path]),
                    percent_entry=100*len([v for v in visitor_sessions if v.entry_page==path])/visitors,
                    percent_exit=100*len([v for v in visitor_sessions if v.exit_page==path])/visitors))
    return result
    
def compute_hourly_entry_exit_page_stats(timestamp):
    start, end = get_hourly_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        for stat in get_all_visited_pages(adomain, start, end):
            DomainPageHourlyStats(**stat).save()
    print start, end

def compute_daily_entry_exit_page_stats(timestamp):
    start, end = get_daily_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        for stat in get_all_visited_pages(adomain, start, end):
            DomainPageDailyStats(**stat).save()
    return start, end

#
# Geolocation Analysis
#
def get_visitor_country_stats(adomain, start, end):
    page_views = list(PageView.objects.filter(adomain=adomain, timestamp__gte=start, timestamp__lt=end, visitor_session__end__isnull=False))
    countries = set([p.visitor_session.country for p in page_views])
    visitor_sessions = set([p.visitor_session for p in page_views])
    visitors = len(visitor_sessions)
    result = []
    for country in countries:
        if country is None: country = Country.objects.get(pk=1)
        coutry_visitors = len([v for v in visitor_sessions if v.country == country])
        result.append(dict(adomain=adomain, timestamp=start, country=country, 
                           pageviews=len([p for p in page_views if p.visitor_session.country==country]), 
                           visitors = coutry_visitors, percent_visitors=100*coutry_visitors/visitors))
    return result

def get_visitor_city_stats(adomain, start, end):
    page_views = list(PageView.objects.filter(adomain=adomain, timestamp__gte=start, timestamp__lt=end, visitor_session__end__isnull=False))
    cities = set([p.visitor_session.city for p in page_views])
    visitor_sessions = set([p.visitor_session for p in page_views])
    visitors = len(visitor_sessions)
    result = []
    for city in cities:
        if city is None: city = 'Unknown'
        city_visitors = len([v for v in visitor_sessions if v.city == city])
        result.append(dict(adomain=adomain, timestamp=start, city=city, 
                           pageviews=len([p for p in page_views if p.visitor_session.city==city]), 
                           visitors=city_visitors, percent_visitors=100*city_visitors/visitors))
    return result

def compute_hourly_country_stats(timestamp):
    start, end = get_hourly_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        for stat in get_visitor_country_stats(adomain, start, end):
            VisitorCountryHourlyStats(**stat).save()
    return start, end

def compute_daily_country_stats(timestamp):
    start, end = get_daily_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        for stat in get_visitor_country_stats(adomain, start, end):
            VisitorCountryDailyStats(**stat).save()
    return start, end

def compute_hourly_city_stats(timestamp):
    start, end = get_hourly_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        for stat in get_visitor_city_stats(adomain, start, end):
            VisitorCityHourlyStats(**stat).save()
    return start, end

def compute_daily_city_stats(timestamp):
    start, end = get_daily_iterval(timestamp)
    for adomain in AccountDomain.objects.all():
        for stat in get_visitor_city_stats(adomain, start, end):
            VisitorCityDailyStats(**stat).save()
    return start, end
#
# Live Page View Information
#
def live_pageview_stats(adomain):
    now = timezone.now()
    stats = {}
    
    hourly = get_domain_page_view_stats(adomain, now.replace(minute=0, second=0))
    stats['this-hour'] = get_domain_page_view_stats(adomain, now.replace(minute=0, second=0))
    stats['this-day'] = get_domain_page_view_stats(adomain, now.replace(hour=0, minute=0, second=0))
    stats['this-week'] = get_domain_page_view_stats(adomain, now.replace(day=1, hour=0, minute=0, second=0))# todo
    stats['this-month'] = get_domain_page_view_stats(adomain, now.replace(day=1, hour=0, minute=0, second=0))
    return stats

