# -*- coding: utf-8 -*-


from django.contrib import admin
from models import *
from django.contrib.sessions.models import Session

admin.site.register(Account)
admin.site.register(AccountDomain)
admin.site.register(Visitor)
admin.site.register(VisitorSession)
admin.site.register(PageView)
admin.site.register(VisitorPageviewTenMinuteStats)
admin.site.register(VisitorPageviewHourlyStats)
admin.site.register(VisitorPageviewDailyStats)
admin.site.register(Session)

admin.site.register(DomainPageHourlyStats)
admin.site.register(DomainPageDailyStats)
admin.site.register(VisitorCountryHourlyStats)
admin.site.register(VisitorCountryDailyStats)
admin.site.register(VisitorCityHourlyStats)
admin.site.register(VisitorCityDailyStats)
admin.site.register(Country) 
