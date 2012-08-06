# -*- coding: utf-8 -*-

import datetime
from django.utils.timezone import utc

def datetime2millis(timestamp):
    delta = timestamp.replace(tzinfo=utc) - datetime.datetime(1970, 1, 1).replace(tzinfo=utc)
    return (delta.days * 24 * 60 * 60 + delta.seconds) * 1000 # + delta.microseconds/1000

def millis2datetime(millisecs): 
    return datetime.datetime(1970, 1, 1).replace(tzinfo=utc) + datetime.timedelta(seconds=millisecs/1000)

def dtrange(start, end, timedelta):
    result = [start]
    _next = start+timedelta
    while _next <= end:
        result.append(_next)
        _next += timedelta
    return result

