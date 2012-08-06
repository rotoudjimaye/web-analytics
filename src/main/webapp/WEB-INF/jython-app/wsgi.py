#!/usr/bin/env python
from __future__ import with_statement
from __future__ import division

import os, sys, traceback

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

def handler(*args, **kwargs):
    try:
        return application(*args, **kwargs)
    except Exception, e:
        print traceback.format_exc()
        raise


