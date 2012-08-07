# -*- coding: utf-8 -*-
""" 
WebAnalytics webanalytics views.py
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.core.servers.basehttp import FileWrapper
from django.utils import timezone
import pytz

from models import *
from forms import *
from json_templates import *
from utils import render_ext

import os.path
import datetime
#import requests
import simplejson
from django.conf import settings
import datetime_utils
import traceback
from accounts.views import logout

from djangojy import jyquartz

class JsonResponse(HttpResponse):
    def __init__(self, *args, **kwargs):
        kwargs.update(dict(mimetype="application/json"))
        super(JsonResponse, self).__init__(*args, **kwargs)

#
def extend_session_timeout(req): 
    """ extends the django session duration (to keep longer track of visitors) """
    req.session.set_expiry(31536000)


# max minutes between two consecutive page views in a session
MAX_PAGEVIEW_INTERVAL_MINUTES = 120

def get_visitor(session_key, user_agent, lang):
    """ returns the Visitor tied to the HTTP request"""
    try:
        visitor = Visitor.objects.get(session=session_key)
    except Visitor.DoesNotExist:
        visitor = Visitor(session=session_key, useragent=user_agent, language = lang)
        visitor.save()
    return visitor

def geolocate_ip_address(ip):
    try:
        rq = requests.get("http://api.hostip.info/get_json.php?position=true&ip="+ip)
        json = simplejson.loads(rq.text)
        try: 
            country = Country.objects.get(code=json["country_code"])
        except Exception, e:
            country = Country(code=json['country_code'], name=json['country_name'])
            country.save()
        city = json['city'] if json.get('city') else 'Unknown';
        return country, "%s - %s"%(country.code, city)
    except Exception, e:
        print "...error when retrieving ip geolocation:", e
        if not list(Country.objects.filter(code='Unknown')): 
            Country(code='Unknown', name='Uknown').save()
        return Country.objects.get(code='Unknown'), 'Unknown'

def get_previous_page_view(visitor, domain, hit_timestamp):
    idle_since = hit_timestamp + datetime.timedelta(minutes=-MAX_PAGEVIEW_INTERVAL_MINUTES)
    previous_pageviews = PageView.objects.filter(visitor=visitor, browser_hostname=domain, timestamp__gte=idle_since).order_by("-timestamp")
    if previous_pageviews:
        return previous_pageviews[0]
    return None

@jyquartz.async()
def save_form_async(page_view, session_key, account_id):
    deserialized_page_view = page_view
    page_view = deserialized_page_view.object
    visitor = get_visitor(session_key, page_view.visitor_useragent, page_view.visitor_language)
    account = Account.objects.get(uuid=account_id)
    domain = page_view.browser_hostname
    try:
        accntdomain = AccountDomain.objects.get(account=account, domain=domain)
    except AccountDomain.DoesNotExist:
        print ":::!!!!!!!!! AccountDomain not found for (account: %s, domain: %s)" % (account, domain)
        return
    country, city = geolocate_ip_address(page_view.visitor_ip)
    page_view.visitor_city = city
    page_view.visitor_country = country.code if country else None
    previous_pageview = get_previous_page_view(visitor, page_view.browser_hostname, page_view.timestamp)
    page_view.adomain = accntdomain
    page_view.visitor = visitor
    if previous_pageview is not None:
        visitor_session = previous_pageview.visitor_session
    else:
        visitor_session = VisitorSession(visitor=visitor, start=page_view.timestamp, domain=page_view.browser_hostname, country=country, city=city,
            referer=page_view.browser_referer, entry_page=page_view.browser_pathname, visitor_ip=page_view.visitor_ip)
        visitor_session.save()
    page_view.visitor_session = visitor_session
    page_view.save()
    #
    session_pageviews = list(PageView.objects.filter(visitor_session=visitor_session))
    if len(session_pageviews) > 1:
    # update visitor session information
        visitor_session.end = max([p.timestamp for p in session_pageviews])
        visitor_session.exit_page = page_view.browser_pathname
        visitor_session.duration = (visitor_session.end - visitor_session.start).seconds
        visitor_session.page_views = len(session_pageviews)
        visitor_session.save()
    print ":::Saved page view", page_view

def process_pageview(req):
    if req.GET:
        form = PageViewForm(req.GET)
        if form.is_valid():  
            page_view = form.save(commit=False)
            account_id = form.cleaned_data['account_id']
            page_view.visitor_ip = req.META.get('REMOTE_ADDR')
            page_view.visitor_hostname = req.META.get('REMOTE_HOST')
            page_view.visitor_useragent = req.META.get('HTTP_USER_AGENT')
            page_view.visitor_language = req.META.get('HTTP_ACCEPT_LANGUAGE')
            timestamp = timezone.now()
            page_view.visitor_tz = 'GMT+1'
            page_view.timestamp = timestamp
            page_view.visitor_localtime = timestamp # TODO: fix
            page_view.visitor_referer = req.META.get('HTTP_REFERER')
            save_form_async(page_view=page_view, session_key=req.session.session_key, account_id=account_id).execute()
            return 'success', {'page_view': page_view, 'session': req.session}
        else:
            return 'error', {'message': "invalid data", 'errors': form.errors}
    return 'success', {}


def hit(request):
    try:
        extend_session_timeout(request)
        process_pageview(request)
    except Exception, e: 
        print "PageView processing failed:", e
        print traceback.format_exc()
    filename = os.path.join(settings.PROJECT_DIR, "media/images/webanalytics.gif")
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='image/gif')
    response['Content-Length'] = os.path.getsize(filename)   
    return response

def validate_user(request):
    if not request.session.get('account_id'):
        logout(request)
        return False
    return True

def home(request):
    return HttpResponseRedirect("/analytics/home/")

@login_required
def app_about(request):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    return render(request, "about.html", {})

@login_required()
def account_home(request):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    account = Account.objects.get(pk=request.session['account_id'])
    domains = list(AccountDomain.objects.filter(account=account))
    return render_to_response("account_home.html", {'account': account, 'domains':  domains})

## snippets
@login_required()
def snippet_basic_dashboard(request):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    return render_to_response("snippets/basic-dashboard.html")

@login_required()
def snippet_entry_exit_dashboard(request):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    return render_to_response("snippets/entry-exit-dashboard.html")

@login_required()
def snippet_geolocation_dashboard(request):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    return render_to_response("snippets/geolocation-dashboard.html")


## reporting
def get_adomain(request):
    account = Account.objects.get(pk=request.session['account_id'])
    if request.GET.get('domain'): return AccountDomain.objects.get(account=account, domain=request.GET['domain'])
    else: return AccountDomain.objects.filter(account=account)[0]

    
def request_tz(request):
    return request.session.get("__user_timezone")

def millis2datetime(millisecs, request):
    tz = pytz.timezone(request.session.get("__user_timezone") or settings.TIME_ZONE)
    return datetime_utils.millis2datetime(long(millisecs), tz)

@login_required()
def reporting_pageview(request, frequency):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    adomain = get_adomain(request) 
    latest = request.GET.get('latest')
    if frequency == "minutely":
        return JsonResponse(get_ten_minute_stats_history(adomain, millis2datetime(latest, request)))
    if frequency == "hourly":
        return JsonResponse(get_hourly_stats_history(adomain, millis2datetime(latest, request)))
    if frequency == "daily":
        return JsonResponse(get_daily_stats_history(adomain, millis2datetime(latest, request)))
    return JsonResponse("{}")


## reporting
@login_required()
def reporting_top_cities(request, frequency):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    adomain = get_adomain(request) 
    latest = request.GET.get('latest')
    if frequency == "hourly":
        return JsonResponse(get_city_stats_hourly(adomain, millis2datetime(latest, request)))
    if frequency == "daily":
        return JsonResponse(get_city_stats_daily(adomain, millis2datetime(latest, request)))
    return JsonResponse("{}")

@login_required()
def reporting_top_countries(request, frequency):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    adomain = get_adomain(request) 
    latest = request.GET.get('latest')
    if frequency == "hourly":
        return JsonResponse(get_country_stats_hourly(adomain, millis2datetime(latest, request)))
    if frequency == "daily":
        return JsonResponse(get_country_stats_daily(adomain, millis2datetime(latest, request)))
    return JsonResponse("{}")

@login_required()
def reporting_top_entry_pages(request, frequency):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    adomain = get_adomain(request) 
    latest = request.GET.get('latest')
    if frequency == "hourly":
        return JsonResponse(get_top_entry_pages_stats_hourly(adomain, millis2datetime(latest, request)))
    if frequency == "daily":
        return JsonResponse(get_top_entry_pages_stats_daily(adomain, millis2datetime(latest, request)))
    return JsonResponse("{}", mimetype="application/json")

@login_required()
def reporting_top_exit_pages(request, frequency):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    adomain = get_adomain(request) 
    latest = request.GET.get('latest')
    if frequency == "hourly":
        return JsonResponse(get_top_entry_pages_stats_hourly(adomain, millis2datetime(latest, request)))
    if frequency == "daily":
        return JsonResponse(get_top_entry_pages_stats_daily(adomain, millis2datetime(latest, request)))
    return JsonResponse("{}")


import csv

def csv_response(data, columns, file_name):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename='+file_name
    writer = csv.writer(response)
    writer.writerow([field[1] for field in columns])
    for item in list(data):
        writer.writerow([(getattr(item, field[0]) if not callable(field[0]) else field[0](item)) for field in columns])
    return response

@login_required()
def download_csv(request, data, frequency):
    if not validate_user(request):
        return HttpResponseRedirect("/accounts/login/")
    adomain = get_adomain(request) 
    if data == "pageview":
        if frequency == "minutely": 
            start = timezone.now() + datetime.timedelta(hours=-6)
            return csv_response(VisitorPageviewTenMinuteStats.objects.filter(timestamp__gt=start, adomain=adomain).order_by("timestamp"),
                                [(lambda e: e.adomain.domain, 'Domain'), ('timestamp','Date'), 
                                 ('visitors', 'Visitors'), ('pageviews', 'Page Views'), ('avg_visit_duration', 'Avg Duration') ],
                                "page_views_ten_minutely.csv")
        if frequency == "hourly": 
            start = timezone.now() + datetime.timedelta(hours=-24)
            return csv_response(VisitorPageviewHourlyStats.objects.filter(timestamp__gt=start, adomain=adomain).order_by("timestamp"),
                                [(lambda e: e.adomain.domain, 'Domain'), ('timestamp','Date'), 
                                 ('visitors', 'Visitors'), ('pageviews', 'Page Views'), ('avg_visit_duration', 'Avg Duration') ],
                                "page_views_hourly.csv")
        if frequency == "daily": 
            start = timezone.now() + datetime.timedelta(days=-30)
            return csv_response(VisitorPageviewDailyStats.objects.filter(timestamp__gt=start, adomain=adomain).order_by("timestamp"),
                                [(lambda e: e.adomain.domain, 'Domain'), ('timestamp','Date'), 
                                 ('visitors', 'Visitors'), ('pageviews', 'Page Views'), ('avg_visit_duration', 'Avg Duration') ],
                                "page_views_daily.csv")
    return HttpResponse("Bad Request")