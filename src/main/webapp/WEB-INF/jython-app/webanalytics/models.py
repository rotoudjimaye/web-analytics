#-*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth import models as authmodels
from django.utils.translation import ugettext as _


class Account(models.Model):
    """ A webanalytics Account """
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(authmodels.User)
    uuid = models.CharField(_("Account ID"), max_length=255, unique=True)
    def __unicode__(self):
        return "Account{user: %s, uuid: %s}" % (self.user, self.uuid)

class AccountDomain(models.Model):
    """ Domain set to be monitored for an account """
    created = models.DateTimeField(auto_now=True)
    account = models.ForeignKey(Account)
    domain = models.CharField(_("Website Visited"), max_length=255, unique=True)
    #class Meta:
    #    unique_together = ("account", "domain")   
    def __unicode__(self):
        return u"AccountDomain{account: %s, domain: %s}" %(self.account.user, self.domain)

class Visitor(models.Model):
    """ A visitor record, which maps to a unique session """
    session = models.CharField(_("Visitor Session Key"), max_length=255, unique=True)
    useragent = models.CharField(_("Browser User Agent"), max_length=255, null=True, blank=True)
    language = models.CharField(_("Visitor's Language"), max_length=64, null=True, blank=True)
    operating_system = models.CharField(_("Visitor Operating System"), max_length=255, null=True, blank=True)
    browser_name = models.CharField(_("Visitor Browser"), max_length=255, null=True, blank=True)
    browse_version = models.CharField(_("Visitor Browser Version"), max_length=255, null=True, blank=True)
    def __unicode__(self):
        return u"Visitor{id: %d, session: %s}" % (self.id, self.session, )

class Country(models.Model):
    code = models.CharField(_("Country Code"), max_length=10, unique=True)
    name =  models.CharField(_("Country Name"), max_length=255, null=True, blank=True)
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code)

class VisitorSession(models.Model):
    visitor = models.ForeignKey(Visitor)
    domain = models.CharField(_("Visited Domain"), max_length=255, db_index=True)
    start = models.DateTimeField("Session start")
    end = models.DateTimeField("Session end", null=True, blank=True)
    duration = models.IntegerField(_("Duration"), default=0)
    page_views = models.IntegerField(_("Page Views"), default=0)
    entry_page = models.CharField(_("Visit entry page"), max_length=255, null=True, blank=True)
    referer = models.CharField(_("HTTP Referer of entry page"), max_length=255, null=True, blank=True)
    exit_page = models.CharField(_("Visit exit page"), max_length=255, null=True, blank=True)
    visitor_ip = models.IPAddressField(_("Visitor IP Address"), max_length=64, blank=True)
    lattitude = models.CharField(_("Geographic location (lat)"), max_length=255, null=True, blank=True)
    longitue = models.CharField(_("Geographic location (long)"), max_length=255, null=True, blank=True)
    country = models.ForeignKey(Country, null=True)
    city = models.CharField(_("City Code"), max_length=255, null=True, blank=True)
    def is_complete(self):
        return self.end is not None
    def __unicode__(self):
        return u"VisitorSession{id: %d, session-key: %s, domain: %s}" % (self.id, self.visitor.session, self.domain)


class PageView(models.Model):
    """ A page View record """
    adomain = models.ForeignKey(AccountDomain)
    visitor = models.ForeignKey(Visitor)
    visitor_session = models.ForeignKey(VisitorSession)
    timestamp = models.DateTimeField("Page View Timestamp")
    visitor_useragent = models.CharField(_("Visitor Browser (User Agent)"), max_length=255, null=True, blank=True)
    visitor_language = models.CharField(_("Visitor's Language"), max_length=64, null=True, blank=True)
    visitor_ip = models.IPAddressField(_("Visitor IP Address"), max_length=64, blank=True)
    visitor_hostname = models.CharField(_("Browser location.hostname"), max_length=255, null=True, blank=True)
    visitor_city = models.CharField(_("Visitor's city"), max_length=255, null=True, blank=True)
    visitor_country = models.CharField(_("Visitor's Country"), max_length=255, null=True, blank=True)
    visitor_tz = models.CharField(_("User Time Zone"), max_length=64, null=True, blank=True)
    visitor_localtime = models.DateTimeField(_("Page View"), null=True, blank=True)
    browser_host = models.CharField(_("Browser location.host"), max_length=255, db_index=True)
    browser_hostname = models.CharField(_("Browser location.hostname"), max_length=255, null=True, db_index=True)
    browser_href = models.CharField(_("Browser location.href"), max_length=255, null=True, blank=True)
    browser_hash = models.CharField(_("Browser location.hash"), max_length=255, null=True, blank=True)
    browser_pathname = models.CharField(_("Browser location.pathname"), max_length=255, null=True, blank=True)
    browser_port = models.CharField(_("Browser location.port"), max_length=255, null=True, blank=True)
    browser_protocol = models.CharField(_("Browser location.protocol"), max_length=255, null=True, blank=True)
    browser_search = models.CharField(_("Browser location.search"), max_length=255, null=True, blank=True)
    browser_referer = models.CharField(_("The HTTP request referer header"), max_length=255, null=True, blank=True)
    def __unicode__(self):
        return "PageView{id: %d, domain: %s, visitor_session: %d}" % (self.id, self.browser_hostname, self.visitor_session.id)

    
class VisitorPageviewTenMinuteStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    timestamp = models.DateTimeField(_("Reporting Hour"))
    visitors = models.IntegerField(_("Number of visitors"), default=0)
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    avg_visit_duration = models.IntegerField(_("Avg visit duration"), default=0)
    avg_pageviews_per_visit = models.IntegerField(_("Page views per visit"), default=0)  
    def __unicode__(self):
        return "VisitorPageviewTenMinuteStats{id: %d, domain: %s, visitors: %d, pageviews: %d, avg_duration: %d, avg_pageviews: %s}"% (
            self.id, self.adomain.domain, self.visitors, self.pageviews, self.avg_visit_duration, self.avg_pageviews_per_visit )  

class VisitorPageviewHourlyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    timestamp = models.DateTimeField(_("Reporting Hour"))
    visitors = models.IntegerField(_("Number of visitors"), default=0)
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    avg_visit_duration = models.IntegerField(_("Avg visit duration"), default=0)
    avg_pageviews_per_visit = models.FloatField(_("Page views per visit"), default=0)
    def __unicode__(self):
        return "VisitorPageviewHourlyStats{id: %d, domain: %s, visitors: %d, pageviews: %d, avg_duration: %d, avg_pageviews: %s}"% (
            self.id, self.adomain.domain, self.visitors, self.pageviews, self.avg_visit_duration, self.avg_pageviews_per_visit ) 

class VisitorPageviewDailyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    timestamp = models.DateTimeField(_("Reporting Day"))
    visitors = models.IntegerField(_("Number of visitors"), default=0)
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    avg_visit_duration = models.IntegerField(_("Avg visit duration"), default=0)
    avg_pageviews_per_visit = models.FloatField(_("Page views per visit"), default=0)
    def __unicode__(self):
        return "VisitorPageviewDailyStats{id: %d, domain: %s, visitors: %d, pageviews: %d, avg_duration: %d, avg_pageviews: %s}"% (
            self.id, self.adomain.domain, self.visitors, self.pageviews, self.avg_visit_duration, self.avg_pageviews_per_visit ) 

class DomainPageHourlyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    pathname = models.CharField(_("Web page path"), max_length=255)
    timestamp = models.DateTimeField(_("Reporting Hour"))
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    percent_entry = models.IntegerField(_("As percent of entry pages"), default=0)
    percent_exit = models.IntegerField(_("As percent of exit pages"), default=0)

class DomainPageDailyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    pathname = models.CharField(_("Web page path"), max_length=255)
    timestamp = models.DateTimeField(_("Reporting Day"))
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    percent_entry = models.IntegerField(_("As percent of entry pages"), default=0)
    percent_exit = models.IntegerField(_("As percent of exit pages"), default=0)

class VisitorCountryHourlyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    timestamp = models.DateTimeField(_("Reporting Day"))
    country = models.ForeignKey(Country)
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    visitors = models.IntegerField(_("Number of visitors"), default=0)
    percent_visitors = models.IntegerField(_("Total Page Views"), default=0)

class VisitorCountryDailyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    timestamp = models.DateTimeField(_("Reporting Day"))
    country = models.ForeignKey(Country)
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    visitors = models.IntegerField(_("Number of visitors"), default=0)
    percent_visitors = models.IntegerField(_("Total Page Views"), default=0)

class VisitorCityHourlyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    timestamp = models.DateTimeField(_("Reporting Day"))
    city = models.CharField(_("City"), max_length=32)
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    visitors = models.IntegerField(_("Number of visitors"), default=0)
    percent_visitors = models.IntegerField(_("Total Page Views"), default=0)

class VisitorCityDailyStats(models.Model):
    adomain = models.ForeignKey(AccountDomain)
    city = models.CharField(_("City"), max_length=32)
    timestamp = models.DateTimeField(_("Reporting Day"))
    pageviews = models.IntegerField(_("Total Page Views"), default=0)
    visitors = models.IntegerField(_("Number of visitors"), default=0)
    percent_visitors = models.IntegerField(_("Total Page Views"), default=0)

