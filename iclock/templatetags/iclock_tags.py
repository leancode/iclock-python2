import datetime
from django import template
from django.conf import settings
from cgi import escape
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from mysite.iclock.datautils import GetModel, hasPerm
from django.db import models
from django.utils.encoding import force_unicode, smart_str

register = template.Library()


@register.inclusion_tag('filters.html')
def filters(cl):
    return {'cl': cl}


def filter(cl, spec):
    return {'title': spec.title(), 'choices': list(spec.choices(cl))}


filter = register.inclusion_tag('admin/filter.html')(filter)


@register.simple_tag
def current_time(format_string):
    return str(datetime.datetime.now())


@register.filter
def HasPerm(user, operation):
    return user.has_perm(operation)


@register.filter
def menuItem(user, operation):
    if not isinstance(user, models.Model):
        user = user.user
    op, dm = operation.split('_')
    model = GetModel(dm)
    if model:
        try:
            iclock_url_rel = user.iclock_url_rel
        except:
            iclock_url_rel = '..'
        else:
            if user.has_perm(operation):
                try:
                    return u'<li><a href="%s/data/%s/">%s</a></li>' % (
                        iclock_url_rel, model.__name__, model._meta.verbose_name.capitalize())
                except:
                    if dm == 'oplog':
                        return u'<li><a href="%s/data/%s/">Registro da opera\xe7\xe3o do dispositivo</a></li>' % (
                            iclock_url_rel, model.__name__)
                    if dm == 'department':
                        return u'<li><a href="%s/data/%s/">Departamento</a></li>' % (iclock_url_rel, model.__name__)
                    if dm == 'employee':
                        return u'<li><a href="%s/data/%s/">Funcion\xe1rio</a></li>' % (iclock_url_rel, model.__name__)
                    if dm == 'transaction':
                        return u'<li><a href="%s/data/%s/">Transa\xe7\xe3o</a></li>' % (iclock_url_rel, model.__name__)
                    if dm == 'devlog':
                        return u'<li><a href="%s/data/%s/">Dados do dispositivo</a></li>' % (
                            iclock_url_rel, model.__name__)
                    if dm == 'devcmds':
                        return u'<li><a href="%s/data/%s/">Comando para dispositivo</a></li>' % (
                            iclock_url_rel, model.__name__)
                    if dm == 'adminlog':
                        return u'<li><a href="%s/data/%s/">Registro da administra\xe7\xe3o</a></li>' % (
                            iclock_url_rel, model.__name__)
                    return u'<li><a href="%s/data/%s/">%s</a></li>' % (
                        iclock_url_rel, model.__name__, model._meta.verbose_name.capitalize())

            else:
                try:
                    return u'<li>&nbsp;&nbsp;%s</li>' % model._meta.verbose_name.capitalize()
                except:
                    if dm == 'oplog':
                        return u'<li>&nbsp;&nbsp;Registro da opera\xe7\xe3o do dispositivo</li>'
                    if dm == 'department':
                        return u'<li>&nbsp;&nbsp;Departamento</li>'
                    if dm == 'employee':
                        return u'<li>&nbsp;&nbsp;Funcion\xe1rio</li>'
                    if dm == 'transaction':
                        return u'<li>&nbsp;&nbsp;Transa\xe7\xe3o</li>'
                    if dm == 'devlog':
                        return u'<li>&nbsp;&nbsp;Dados do dispositivo</li>'
                    if dm == 'devcmds':
                        return u'<li>&nbsp;&nbsp;Comando para dispositivo</li>'
                    if dm == 'adminlog':
                        return u'<li>&nbsp;&nbsp;Registro da administra\xe7\xe3o</li>'
                    return u'<li>&nbsp;&nbsp;%s</li>' % model._meta.verbose_name.capitalize()

    return ''


@register.filter
def opMenuItem(user, operation):
    if user.has_perm(operation):
        return u'<li><a href="%s/data/%s/">%s</a></li>' % (
            iclock_url_rel, model.__name__, model._meta.verbose_name.capitalize())
    return u'<li>' + model._meta.verbose_name + '</li>'


@register.filter
def reqHasPerm(request, operation):
    return hasPerm(request.user, request.model, operation)


@register.filter
def buttonItem(request, operation):
    if hasPerm(request.user, request.model, operation):
        return u'<li><a href="%s/data/%s/">%s</a></li>' % (iclock_url_rel, model.__name__, model._meta.verbose_name)
    return u'<li>' + model._meta.verbose_name + '</li>'


@register.simple_tag
def version():
    return settings.VERSION


@register.filter
def cap(s):
    return (u'%s' % s).capitalize()


@register.filter
def enabled_udisk_mod(mod_name):
    return 'udisk' in settings.ENABLED_MOD


@register.filter
def enabled_weather_mod(mod_name):
    return 'weather' in settings.ENABLED_MOD


@register.filter
def enabled_msg_mod(mod_name):
    return 'msg' in settings.ENABLED_MOD


@register.filter
def enabled_att_mod(mod_name):
    return 'att' in settings.ENABLED_MOD


@register.filter
def enabled_mod(mod_name):
    return mod_name in settings.ENABLED_MOD


@register.filter
def lescape(s):
    if not s:
        return ''
    s = escape(s)
    return escape(s).replace('\n', '\\n').replace('\r', '\\r').replace("'", '&#39;').replace('"', '&quot;')


@register.filter
def isoTime(value):
    if value:
        return str(value)[:19]
    if value == 0:
        return '0'
    return ''


@register.filter
def stdTime(value):
    if value:
        return value.strftime(settings.STD_DATETIME_FORMAT)
    return ''


@register.filter
def shortTime(value):
    if value:
        return value.strftime(settings.SHORT_DATETIME_FMT)
    return ''


@register.filter
def vshortTime(value):
    if value:
        return value.strftime(settings.VSHORT_DATETIME_FMT)
    return ''


@register.filter
def shortDTime(value):
    if value:
        return value.strftime(settings.SHORT_DATETIME_FMT2)
    return ''


@register.filter
def onlyTime(value):
    if value:
        try:
            return value.strftime(settings.TIME_FMT)
        except:
            return (value + datetime.timedelta(100)).strftime(settings.TIME_FMT)

    else:
        return ''


@register.filter
def shortDate(value):
    if value:
        return value.strftime(settings.DATE_FMT)
    return ''


@register.filter
def shortDate4(value):
    if value:
        return value.strftime(settings.DATE_FMT4)
    return ''


@register.filter
def left(value, size):
    s = u'%s' % value
    if len(s) > size:
        return s[:size] + ' ...'
    return s


@register.filter
def HasPerm(user, operation):
    return user.has_perm(operation)


@register.filter
def PackList(values, field):
    l = []
    for s in values:
        l.append(s[field])

    return (',').join(l)


def _(s):
    return s


CmdContentNames = {'DATA USER PIN=': _('Personnel information'), 'DATA FP PIN=': _('Fingerprint'),
                   'DATA DEL_USER PIN=': _('Del employee'),
                   'DATA DEL_FP PIN=': _('Del fingerprint'),
                   'CHECK': _('Check the server configuration'),
                   'INFO': _('Updated device information on the server'),
                   'CLEAR LOG': _('Remove transaction'),
                   'RESTART': _('restart device'),
                   'REBOOT': _('reboot device'),
                   'LOG': _('Check and upload the new data'),
                   'PutFile': _('Send file to the device'),
                   'GetFile': _('Get file from the equipment'),
                   'Shell': _('Run a device shell command'),
                   'SET OPTION': _('Change configuration'),
                   'CLEAR DATA': _('Clear all data'),
                   'AC_UNLOCK': _('Output unlock signal'),
                   'AC_UNALARM': _('Terminate alarm signal'),
                   'ENROLL_FP': _("Enroll employee's fingerprint")}


def getContStr(cmdData):
    for key in CmdContentNames:
        if key in cmdData:
            return CmdContentNames[key]

    return ''


@register.filter
def cmdName(value):
    return getContStr(value)


DataContentNames = {'TRANSACT': _('Transaction'),
                    'USERDATA': _('employee info/fingerprint ')}


@register.filter
def dataShowStr(value):
    if value in DataContentNames:
        return value + " <span style='color:#ccc;'>" + DataContentNames[value] + '</span>'
    return value


@register.filter
def cmdShowStr(value):
    return left(value, 30) + " <span style='color:#ccc;'>" + getContStr(value) + '</span>'


@register.filter
def thumbnailUrl(obj):
    try:
        url = obj.getThumbnailUrl()
        if url:
            try:
                fullUrl = obj.getImgUrl()
            except:
                return "<img src='%s' />" % url

            if not fullUrl:
                return "<img src='%s' />" % url
            return "<a href='%s'><img src='%s' /></a>" % (fullUrl, url)
    except:
        pass

    return ''
