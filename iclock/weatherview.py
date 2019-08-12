from mysite.iclock.models import *
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
from mysite.iclock.weather import getWeather, checkWeatherForDev
import datetime
from django.utils.translation import ugettext_lazy as _


def genWeatherDev(sn=''):
    if sn:
        Device = getDevice(sn)
        checkWeatherForDev(Device)
        i = 1
    i = 0
    last = ('%s' % (datetime.datetime.now() - datetime.timedelta(0, 172800)))[:19]
    for device in iclock.objects.exclude(DelTag=1).exclude(State=DEV_STATUS_PAUSE).exclude(LastActivity__lt=last):
        checkWeatherForDev(device)
        i += 1

    return i


def index(request, device):
    if device and device[-1] == '/':
        device = device[:-1]
    genWeatherDev(device)
    resp = HttpResponse(_('device:') + device + '\n\n', mimetype='text/plain')
    return resp


def get(request, device):
    if device[-1] == '/':
        device = device[:-1]
    resp = HttpResponse('', mimetype='text/plain')
    resp['Content-Type'] = 'text/plain; charset=utf-8'
    w = getWeather(device)
    resp.write((u'\n').join(w))
    return resp
