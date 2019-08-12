from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change
import os, time
from mysite.iclock.models import iclock, department, employee, fptemp, devlog, transaction, devcmds
from settings import MEDIA_ROOT, ADDITION_FILE_ROOT, LOGIN_REDIRECT_URL
from django.template import loader, Context, RequestContext
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response
from mysite.utils import *
from django.contrib import admin
from mysite.staticfiles import serve

admin.autodiscover()


def index(request):
    return HttpResponseRedirect(LOGIN_REDIRECT_URL)


def my_i18n(request):
    from django.views.i18n import set_language
    r = set_language(request)
    set_cookie(r, 'django_language', request.REQUEST['language'], 31536000)
    return r


def image(request):
    raw = request.raw_post_data
    time.sleep(100)
    return render_to_response('index.html', RequestContext(request, {}))


urlpatterns = patterns('', (
    'iclock/i18n/setlang/', my_i18n), (
                           'iclock/rosetta-i18n/', include('rosetta.urls')), (
                           'iclock/file/(?P<path>.*)$', serve,
                           {'document_root': ADDITION_FILE_ROOT, 'show_indexes': True}), (
                           'iclock/tmp/(?P<path>.*)$', serve, {'document_root': tmpDir(), 'show_indexes': True}), (
                           'iclock/ccccc/(?P<path>.*)$', serve, {'document_root': 'c:/', 'show_indexes': True}), (
                           'iclock/media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT, 'show_indexes': False}), (
                           'iclock/accounts/', include('mysite.authurls')), (
                           'iclock/', include('mysite.iclock.urls')), (
                           '^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT, 'show_indexes': True}),
                       ('^options/',
                        'mysite.iclock.setoption.index'), (
                           '^image', image), (
                           '^admin/(.*)', admin.site.root), (
                           '^photologue/', include('django_apps.photologue.urls')), (
                           '^$', index))
