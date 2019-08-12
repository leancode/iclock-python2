from mysite.iclock.models import *
from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import string, datetime, time
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from mysite.cab import *
from mysite.iclock import reb
import os, time
from mysite.iclock.dataproc import *
from django.conf import settings
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext


def AppendUserDev(dispEmp, SNs, cursor):
    needSave = False
    try:
        pin = formatPIN(dispEmp[0])
        try:
            e = employee.objects.get(PIN=pin)
            if e.SN and SNs != settings.ALL_TAG and e.SN.SN not in SNs:
                return _('No permission to do on device %s!') % e.SN.SN
        except:
            e = employee(PIN=pin, DeptID=getDefaultDept())
            needSave = True
        else:
            try:
                device = getDevice(dispEmp[1])
                if SNs != settings.ALL_TAG and device.SN not in SNs:
                    return _('No permission to download employee data to device %s!') % device.SN
            except:
                if dispEmp[1]:
                    return _('Designated device does not exist!')
                if SNs != settings.ALL_TAG:
                    return _('Not specified a device!')
                device = None
            else:
                if not e.DeptID:
                    e.DeptID = getDefaultDept()
                    needSave = True
                if device and not e.SN:
                    e.SN = device
                    needSave = True
                if needSave:
                    e.save()

            if not device:
                return
            appendDevCmd(device, getEmpCmdStr(e))
            for afp in fptemp.objects.filter(UserID=e):
                appendDevCmd(device, u'DATA UPDATE FINGERTMP PIN=%s\tFID=%d\tSize=%d\tValid=%d\tTMP=%s' % (
                    e.pin(), afp.FingerID, 0, afp.Valid, afp.temp()))

    except Exception, e:
        errorLog()
        return '%s' % e

    return


def DelUserDev(dispEmp, SNs, cursor):
    try:
        pin = formatPIN(dispEmp[0])
        try:
            e = employee.objects.get(PIN=pin)
            if not e.DeptID:
                return _('Designated employee does not exist!')
        except:
            return _('Designated employee does not exist!')
        else:
            try:
                device = getDevice(dispEmp[1])
                if SNs != settings.ALL_TAG and device.SN not in SNs:
                    return _("No permission to deete the employee's in device %s") % device
            except:
                if dispEmp[1]:
                    return _('Designated device does not exist!')
                if SNs != settings.ALL_TAG and (not e.SN or e.SN_id not in SNs):
                    if e.SN:
                        return _('Not specified a device, and no permission to delete employee from device %s.') % e.SN
                    return _('Not specified a device, and the employee has no a enrollment device.')
                device = None

        delEmpFromDev(SNs == settings.ALL_TAG, e, device)
    except Exception, e:
        return '%s' % e

    return


def NameUserDev(dispEmp, SNs, cursor):
    newUser = False
    assignDev = False
    try:
        device = getDevice(dispEmp[2])
    except:
        device = None
    else:
        try:
            userName = dispEmp[1]
        except:
            userName = u''

    try:
        pin = dispEmp[0]
        if len(pin) != PIN_WIDTH or not pin.isdigit() or int(pin, 10) in DISABLED_PINS:
            return _('%s is not a valid PIN.') % pin
        try:
            e = employee.objects.get(PIN=pin)
        except:
            e = employee(PIN=pin, EName=userName, DeptID=getDefaultDept())
            if device:
                e.SN = device
            e.save()
            newUser = True
        else:
            if not e.DeptID or userName and userName != e.EName or device and not e.SN:
                e.DeptID = getDefaultDept()
                e.EName = userName
                if not e.SN:
                    assignDev = True
                    e.SN = device
                e.save()
            userName = e.EName
            if not device:
                device = e.SN

        if not device:
            return _('Not specified a valid device, or the employee has no a enrollment device!')
        if not newUser and not userName:
            return _('The employee no in the database.')
        backDev = device.BackupDevice()
        sql = u'DATA UPDATE USERINFO PIN=%s\tName=%s' % (e.pin(), e.EName)
        appendDevCmd(device, sql, cursor)
        if backDev:
            appendDevCmd(backDev, sql, cursor)
        if assignDev:
            for afp in fptemp.objects.filter(PIN=e):
                sql = u'DATA UPDATE FINGERTMP PIN=%s\tFID=%d\tSize=%d\tValid=%d\tTMP=%s' % (
                    e.pin(), afp.FingerID, 0, afp.Valid, afp.temp())
                appendDevCmd(device, sql, cursor)
                if backDev:
                    appendDevCmd(backDev, sql, cursor)

    except Exception, e:
        return '%s' % e

    return


def disp_emp(request, delemp):
    from django.db import connection as conn
    cursor = conn.cursor()
    task = delemp and u'deluser' or request.path.find('name_emp') >= 0 and u'username' or u'userinfo'
    titles = {'deluser': _('Delete employee from device'), 'username': _("Download employee's name to device"),
              'userinfo': _('Dispatch employee to device')}
    title = titles[task]
    if not request.method == 'POST':
        return render_to_response('disp_emp.html', {'title': title, 'task': task})
        cc = u''
        SNs = request.user.is_superuser and settings.ALL_TAG or getUserIclocks(request.user)
        process = task == 'deluser' and DelUserDev or task == 'userinfo' and AppendUserDev or NameUserDev
        errorLines = []
        i = 0
        okc = 0
        f = request.FILES['fileUpload']
        lines = ''
        for chunk in f.chunks():
            lines += chunk

        lines = lines.decode('GBK').split('\n')
        for line in lines:
            i += 1
            if line:
                if line[-1] in ('\r', '\n'):
                    line = line[:-1]
            if line:
                if line[-1] in ('\r', '\n'):
                    line = line[:-1]
            try:
                if line:
                    if line.find('\t') >= 0:
                        data = (line + '\t').split('\t')
                    else:
                        if line.find(',') >= 0:
                            data = (line + ',').split(',')
                        else:
                            data = (line + ' ').split(' ', 1)
                    error = process(data, SNs, cursor)
                    if error:
                        errorLines.append(u'Line %d(%s):%s' % (i, line, error))
                    okc += 1
            except Exception, e:
                errorLines.append(u'Line %d(%s):%s' % (i, line, str(e)))

        if okc:
            conn._commit()
        if len(errorLines) > 0 and okc > 0:
            cc += _("%s employee's data is ready to transfer, but following record(s) is missing:") % okc + '</p><pre>'
        else:
            cc += _('There are wrong: ') + '</p><pre>'
        cc += (u'\n').join(errorLines)
        cc += u'</pre>'
    else:
        cc += _('%s employee(s) data is ready to transfer.') % okc
    return render_to_response('info.html', {'title': title, 'content': cc})


@login_required
def FileDelEmp(request):
    return disp_emp(request, True)


@login_required
def FileChgEmp(request):
    return disp_emp(request, False)


@login_required
def disp_emp_log(request):
    return render_to_response('disp_emp_log.html', {'title': _('Dispatch employee data to device')})


def saveUser(pin, pwd, ename, card, grp, tzs):
    try:
        e = employee.objects.get(PIN=pin)
    except:
        e = employee(PIN=pin, DeptID=getDefaultDept())
    else:
        if ename:
            e.EName = unicode(ename, 'gb2312')
        if pwd:
            e.Password = pwd
        if grp:
            e.AccGroup = grp
        if tzs:
            e.TimeZones = tzs

    e.save()


def saveFTmp(pin, fid, tmp):
    try:
        t = fptemp.objects.get(PIN=employee.objects.get(PIN=pin), FingerID=fid)
        if t.Template != tmp:
            t.Template = tmp
            t.save()
    except:
        t = fptemp(PIN=employee.objects.get(PIN=pin), FingerID=fid, Valid=1, Template=tmp)
        t.save()


@login_required
def app_emp(request):
    if not request.method == 'POST':
        return render_to_response('disp_emp.html', {'title': _('Upload employee list'), 'task': 'userinfo'})
    i = 0
    f = request.FILES['fileUpload']
    data = ''
    for chunk in f.chunks():
        data += chunk

    lines = data.splitlines()
    pin, ename, pwd, card, grp, tzs = ('', '', '', '', '1', '')
    userTmp = []
    for line in lines:
        if line.find('[Users_') == 0:
            i += 1
            if len(pin) > 0:
                saveUser(pin, pwd, ename, card, grp, tzs)
                for tmp in userTmp:
                    saveFTmp(pin, tmp['fid'], tmp['tmp'])

            pin = line[7:-1]
            ename, pwd, card, grp, tzs = ('', '', '', '1', '')
            userTmp = []
        elif line.find('Name=') == 0:
            ename = line[5:]
        elif line.find('Password=') == 0:
            pwd = line[9:]
        elif line.find('AccTZ1=') == 0:
            tzs = line[7:]
        elif line.find('Card=') == 0:
            card = line[5:]
        elif line.find('Grp=') == 0:
            grp = line[4:]
        elif line.find('FPT_') == 0:
            ftmp = line.split('=')
            fid = ftmp[0][4:]
            userTmp.append({'fid': fid, 'tmp': ftmp[1]})

    if len(pin) > 0:
        saveUser(pin, pwd, ename, card, grp, tzs)
        for tmp in userTmp:
            saveFTmp(pin, tmp['fid'], tmp['tmp'])

    response = HttpResponse(mimetype='text/plain')
    response.write(gettext('%(object)s employee has been successfully!') % {'object': i})
    return response


@login_required
def del_emp_log(request):
    return render_to_response('disp_emp_log.html',
                              {'title': gettext('Delete the employee(s) in device'), 'task': 'deleteuser'})


@login_required
def upgrade(request):
    if not request.method == 'POST':
        return render_to_response('upgrade.html', {'title': gettext('Server upgrades')})
    i = 0
    f = request.FILES['fileUpload']
    bytes = ''
    for chunk in f.chunks():
        bytes += chunk

    target = tmpDir() + '/mysite.zip'
    bkFile = '%s/%s.zip' % (tmpDir(), time.strftime('%Y%m%d%H%M%S'))
    file(target, 'wb+').write(bytes)
    zipDir('c:/mysite/', bkFile)
    fl = unzipFile(target, 'c:/')
    response = HttpResponse(mimetype='text/plain')
    response.write('BACKUP OLD FILE TO: ' + bkFile + '\r\n' + ('\r\n').join(['%s\t%s' % (fl[f], f) for f in fl.keys()]))
    if fl:
        restartThread('iclock-server').start()
        restartThread('iclock').start()
        restartThread('Apache2').start()
    return response


from gzip import *


def getGZipSize(fname):
    g = GzipFile(filename=fname, mode='rb')
    s = 0
    while True:
        chunk = g.read(1024)
        cs = len(chunk)
        if cs > 0:
            s += cs
        else:
            break

    return s


@login_required
def restartDev(request):
    ip = request.GET.get('IP', '')
    if ip:
        url, fname = getFW(iclock(Style='X938'))
        fwSize = getGZipSize(fname)
        ret = reb.tryDoInDev(ip, ['ls /mnt/mtdblock/main -l', 'reboot'])
        if type(ret).__doc__.find('list') == 0:
            ret = gettext('Restart device successfully: ') + ip + '</p><p>' + (
                    ret[0].find(' %s' % fwSize) < 10 and ret[0] + '</p><p>' + gettext(
                'Its size and standard firmware(%(object_name)s) is inconsistent, Need to upgrade firmware If there is no automatic inspection later firmware update, or manually upgrade firmware') % {
                        'object_name': fwSize or ''})
        else:
            ret = gettext('Failure to restart device:') + ip + '</p><p>' + ret
    else:
        ret = _('Please enter the IP address of the device')
    return render_to_response('info.html', {'title': _('Restart device'), 'content': ret})


@login_required
def autoRestartDev(request):
    iclocks = iclock.objects.filter(LastActivity__lt=datetime.datetime.now() - datetime.timedelta(0, (
            settings.REBOOT_CHECKTIME > 30 and settings.REBOOT_CHECKTIME or 30) * 60))
    ips = updateLastReboot(iclocks)
    rebDevsReal(ips)
    return render_to_response('info.html', {'title': _('Automatically check sluggish device'), 'content': gettext(
        'The device(s) does not connect with the server more than half and an hour: </p><p>') + ('<br />').join(
        [u'%s: %s' % (i, i.IPAddress()) for i in iclocks]) + '</p><p>&nbsp;</p><p>' + (ips and gettext(
        'The system will connect and re-start the following device automaticly: </p><p>') + ('<br />').join(
        ips) or '')})
