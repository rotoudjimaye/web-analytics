#-*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify

class Entry(models.Model):
    user = models.ForeignKey(User)
    pub_date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    body = models.TextField()
    def __unicode__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super(Entry, self).save(*args, **kwargs)

