# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, render_to_response
from django.template import RequestContext
import django.contrib.auth as auth
from forms import *


def login(request):
    if request.GET.get('next'):
        request.session['next'] = request.GET['next']
    form = AccountLoginForm(request.POST) if request.POST else AccountLoginForm()
    if request.POST and form.is_valid():
        cleaned_data = form.clean()
        auth.login(request, cleaned_data['user'])
        request.session['account_id'] = cleaned_data['account'].id
        return HttpResponseRedirect(request.session.pop('next', '/'))
    return render_to_response("account_login.html", {'form': form}, context_instance=RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")