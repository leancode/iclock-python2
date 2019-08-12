from mysite.iclock.models import *
from django.template import loader, Context, RequestContext, Library, Template, Context, TemplateDoesNotExist
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import string, os, datetime, time
from django.db import models
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.utils.encoding import force_unicode, smart_str
from django.contrib.auth.models import User, Permission, Group
from django.utils.translation import ugettext as _
from mysite.iclock.iutils import *
from django.utils.datastructures import SortedDict
from django.core.cache import cache


class adminForm(forms.Form):

    def __init__(self, request, data=None, dataKey=None):
        self.request = request
        try:
            instance = User.objects.get(pk=dataKey)
            isAdd = False
        except:
            instance = None
            isAdd = True
        else:
            self.instance = instance
            opts = User._meta
            self.opts = opts
            exclude = ('user_permissions', 'password', 'is_active')
            if isAdd:
                exclude = exclude + ('last_login', 'date_joined')
            else:
                if request.user.pk == instance.pk:
                    exclude = exclude + ('is_staff', 'is_superuser', 'groups')
            field_list = []
            for f in opts.fields + opts.many_to_many:
                if not f.editable:
                    continue
                if exclude:
                    if f.name in exclude:
                        continue
                    current_value = isAdd or f.value_from_object(instance)
                    formfield = f.formfield(initial=current_value)
                else:
                    formfield = f.formfield()
                if formfield:
                    field_list.append((f.name, formfield))
                    if f.name in ('last_login', 'date_joined'):
                        formfield.widget.attrs['readonly'] = True

            field_list.insert(1, (
                'is_resetPw', forms.BooleanField(label=_('Reset password'), initial=False, required=False)))
            formfield = forms.CharField(widget=forms.PasswordInput, label=_('Password'),
                                        initial=isAdd and '' or '111111')
            field_list.insert(2, ('Password', formfield))
            formfield = forms.CharField(widget=forms.PasswordInput, label=_('Password again'),
                                        initial=isAdd and '' or '111111')
            field_list.insert(3, ('ResetPassword', formfield))
            self.dept = None
            if not isAdd:
                try:
                    self.dept = DeptAdmin.objects.filter(user=instance)[0]
                except:
                    pass

            if self.dept:
                formfield = self.dept._meta.get_field('dept').formfield(initial=self.dept.dept_id)
            formfield = DeptAdmin._meta.get_field('dept').formfield()

        if formfield and (not instance or request.user.pk != instance.pk):
            field_list.insert(4, ('AuthedDept', formfield))
        self.base_fields = SortedDict(field_list)
        forms.Form.__init__(self, data)
        return

    def clean_ResetPassword(self):
        p1 = self.cleaned_data.get('Password', '')
        p2 = self.cleaned_data.get('ResetPassword', '')
        if p1 == p2:
            return p2
        raise forms.ValidationError(_('Must be same as Password'))

    def clean_Password(self):
        p1 = self.cleaned_data.get('Password', '')
        return p1

    def save(self):
        opts = self.opts
        u = self.instance
        try:
            if self.request.user.pk == self.instance.pk:
                u = self.request.user
        except:
            pass
        else:
            if u:
                if self.cleaned_data['is_resetPw']:
                    u.set_password(self.clean_Password())
                if not u:
                    isexist = User.objects.all().filter(username=self.cleaned_data['username'])
                    if isexist:
                        pass
                    else:
                        u = User.objects.create_user(self.cleaned_data['username'], self.cleaned_data['email'],
                                                     self.cleaned_data['Password'])
                for f in opts.fields + opts.many_to_many:
                    if not f.editable:
                        continue
                    if f.name in self.cleaned_data:
                        f.save_form_data(u, self.cleaned_data[f.name])

                u.save()
                if u.is_superuser:
                    return u
                try:
                    did = self.cleaned_data['AuthedDept']
                except:
                    did = None
                    errorLog()
                else:
                    if did:
                        if self.dept and did != self.dept.dept:
                            self.dept.dept = did
                            self.dept.save()
                    else:
                        DeptAdmin(user=u, dept=did).save()
            else:
                if self.dept:
                    self.dept.delete()

        return u


def retUserForm(request, f, isAdd=False):
    request.user.iclock_url_rel = '../../..'
    return render_to_response([User.__name__ + '_edit.html', 'data_edit.html'],
                              RequestContext(request, {'form': f, 'iclock_url_rel': request.user.iclock_url_rel,
                                                       'isAdd': isAdd,
                                                       'dataOpt': User._meta,
                                                       'request': request}))


def doCreateAdmin(request, dataModel, dataKey=None):
    if dataKey == '_new_' and request.user.has_perm('add_user'):
        f = adminForm(request, dataKey=dataKey)
        return retUserForm(request, f, isAdd=True)
    else:
        if dataKey:
            f = adminForm(request, dataKey=dataKey)
            if not f.instance:
                return HttpResponseNotFound(
                    _('Keyword "%(object_name)s" Data do not exist!') % {'object_name': dataKey})
            return retUserForm(request, f)
    return render_to_response('info.html', RequestContext(request, {'content': _('No permission')}))


def doPostAdmin(request, dataModel, dataKey=None):
    f = adminForm(request, data=request.POST, dataKey=dataKey)
    if not f.is_valid():
        return retUserForm(request, f, isAdd=dataKey == '_new_')
    try:
        u = f.save()
        k = 'user_id_%s' % u.pk
        cache.delete(k)
        log = adminLog(User=request.user, model='user', object=f.cleaned_data['username'])
        if dataKey == '_new_':
            log.action = 'Create'
        log.save()
    except:
        return render_to_response('info.html', {'title': u'\u7528\u6237',
                                                'content': u'%s\u7528\u6237\u5df2\u7ecf\u5b58\u5728' % f.cleaned_data[
                                                    'username']})

    return HttpResponseRedirect('../')
