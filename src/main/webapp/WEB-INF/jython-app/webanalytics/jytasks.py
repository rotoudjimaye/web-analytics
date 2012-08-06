# -*- coding: utf-8 -*-
"""
Celery scheduled reporting tasks
"""

#from celery.task import task, periodic_task
#from celery.schedules import crontab

from reporting import *
from django.utils import timezone

from djangojy import jyquartz


@jyquartz.schedule(cron=" 0 0/2 * * * ? ", context=True)
def compute_minute_pageview_stats_task(context):
    print "ctx ", context
    print "...starting 10 minute PageView reporting..."
    compute_minute_pageview_stats(timezone.now())
    print "...completed 10 minute PageView reporting"

@jyquartz.schedule(cron=" 0 0 * * * ?  ")
def compute_hourly_pageview_visit_stats_task():
    print "...starting hourly PageView reporting..."
    compute_hourly_pageview_stats(timezone.now())
    print "...completed hourly PageView reporting"

@jyquartz.schedule(cron=" 0 30 0 * * ? ")
def compute_daily_pageview_visit_stats_task():
    print "...starting daily PageView reporting..."
    compute_daily_pageview_stats(timezone.now())
    print "...completed daily PageView reporting"

@jyquartz.schedule(cron=" 0 0 1 ? * SUN ")
def compute_weekly_pageview_visit_stats_task():
    print "...starting weekly PageView reporting..."
    #compute_minute_pageview_stat(timezone.now())
    print "...completed weekly PageView reporting"

@jyquartz.schedule(cron=" 0 0 0 1 * ? ")
def compute_monthly_pageview_visit_stats_task():
    print "...starting monthly PageView reporting..."
    #compute_minute_pageview_stat(timezone.now())
    print "...completed monthly PageView reporting"
