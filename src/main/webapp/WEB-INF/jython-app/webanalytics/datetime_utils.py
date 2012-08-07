# -*- coding: utf-8 -*-

import datetime
from django.utils import timezone

def datetime2millis(timestamp):
    delta = timestamp.replace(tzinfo=timezone.utc) - datetime.datetime(1970, 1, 1).replace(tzinfo=timezone.utc)
    return (delta.days * 24 * 60 * 60 + delta.seconds) * 1000 # + delta.microseconds/1000

def millis2datetime(millisecs, tz=timezone.utc):
    return timezone.make_aware(datetime.datetime(1970, 1, 1), tz) + datetime.timedelta(seconds=millisecs/1000)

def dtrange(start, end, timedelta):
    result = [start]
    _next = start+timedelta
    while _next <= end:
        result.append(_next)
        _next += timedelta
    return result

