from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.cache import cache
from mysite.iclock.models import *
import string, datetime, time
from mysite.utils import *
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import smart_str
import sys, os
from django.db import connection as conn
from reb import *
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext


def batchOp(request, dataModel, func):
    if request.method == 'POST':
        keys = request.POST.getlist('K')
    else:
        keys = request.GET.getlist('K')
    info = []
    ret = None
    for i in keys:
        d = dataModel.objects.in_bulk([i])
        ret = func(d[d.keys()[0]])
        if '%s' % ret == ret:
            info.append(ret)

    if len(info) > 0:
        return (u',\n').join([u'%s' % f for f in info])
    return ret


dict_del_table = {str(employee): [
    'fptemp'],
    str(iclock): []}


def delData(request, dataModel):
    if request.method == 'POST':
        keys = request.POST.getlist('K')
    else:
        keys = request.GET.getlist('K')
    if dataModel == User:
        for i in keys:
            if i != request.user.id:
                d = dataModel.objects.all().filter(id=i)[0]
                if d.username != request.user.username:
                    d.delete()

    rows = dataModel.objects.filter(pk__in=keys)
    if dataModel == employee:
        for row in rows:
            delEmpFromDev(request.user.is_superuser, row, None)

    for row in rows:
        row.delete()

    return
    for i in keys:
        if dataModel == User:
            d = dataModel.objects.all().filter(username=i)[0]
            d.delete()
        else:
            del_by_fk(dataModel, i)
            d = dataModel.objects.all().filter(pk=i)[0]
            d.delete()

    return


def delAllEmp(request, dataModel):
    if request.method == 'POST':
        keys = request.POST.getlist('K')
    else:
        keys = request.GET.getlist('K')
    for i in keys:
        dataModel.objects.filter(SN=i).delete()


def moveEmpToDev(dev, emp, cursor=None):
    pin = emp.pin()
    device = emp.SN
    if device:
        if dev.SN == device.SN:
            return None
        appendDevCmd(device, 'DATA DELETE USERINFO PIN=%s' % pin, cursor)
        device = emp.SN.BackupDevice()
        if device:
            appendDevCmd(device, 'DATA DELETE USERINFO PIN=%s' % pin, cursor)
    emp.SN = dev
    emp.save()
    return appendEmpToDev(dev, emp, cursor)


def delEmpFromDev(superuser, emp, dev):
    pin = emp.pin()
    if dev:
        return appendDevCmd(dev, 'DATA DELETE USERINFO PIN=%s' % pin)
    if emp.SN:
        bk = emp.SN.BackupDevice()
        if bk:
            appendDevCmd(bk, 'DATA DELETE USERINFO PIN=%s' % pin)
        appendDevCmd(emp.SN, 'DATA DELETE USERINFO PIN=%s' % pin)
    if superuser:
        emp.OffDuty = 1
        emp.save()


def del_by_fk(dataModel, pk, app_label='iclock'):
    table_fk = []
    for row in dir(dataModel.objects.all()[0]):
        r = str(row)
        if r.endswith('_set'):
            table_fk.append(r[:-4])

    if dict_del_table.has_key(str(dataModel)):
        for row in dict_del_table[str(dataModel)]:
            if row in table_fk:
                table_fk.remove(row)

    for row_table in table_fk:
        to_field = dataModel._meta.pk.name
        model_fk = models.get_model(app_label, row_table)
        fields = model_fk._meta.fields
        for row_field in fields:
            if 'ForeignKey' in str(type(row_field)):
                if to_field == row_field.name:
                    rs = eval('model_fk.objects.all().filter(' + to_field + '=pk)')
                    for row_rs in rs:
                        setattr(row_rs, to_field, None)
                        row_rs.save()

    return


def staAData(dObj, state):
    dObj.State = state
    dObj.save()


def staData(request, dataModel, state):
    batchOp(request, dataModel, lambda d: staAData(d, state))


def appendDevCmdOld(dObj, cmdStr, cmdTime=None):
    pushVersion = dObj.PushVersion or 0.0
    pushVersion = float(pushVersion)
    if pushVersion < 2.0:
        cmdStr = cmdStr.replace('DATA UPDATE USERINFO', 'DATA USER')
        cmdStr = cmdStr.replace('DATA UPDATE FINGERTMP', 'DATA FP')
        cmdStr = cmdStr.replace('DATA DELETE USERINFO', 'DATA DEL_USER')
        cmdStr = cmdStr.replace('DATA DELETE FINGERTMP', 'DATA DEL_FP')
        cmdStr = cmdStr.replace('DATA UPDATE SMS', 'DATA SMS')
    cmd = devcmds(SN=dObj, CmdContent=cmdStr, CmdCommitTime=cmdTime or datetime.datetime.now())
    cmd.save()
    return cmd.id


def appendDevCmd(dObj, cmdStr, cursor=None, cmdTime=None):
    appendDevCmdOld(dObj, cmdStr, cmdTime)


def devNoAlarm(dObj, request):
    alarmTimeStart, alarmTimeEnd, alarmEnd = dObj.isInAlarm()
    if not alarmTimeStart:
        return DEV_STATUS_OK
    if datetime.datetime.now() < alarmTimeEnd:
        return DEV_STATUS_WAIT
    appendDevCmd(dObj, 'NOALARM')
    try:
        a = alarms.objects.get(SN=dObj, AlarmTime=alarmTimeEnd)
    except:
        a = alarms(SN=dObj, AlarmTime=alarmTimeStart)
    else:
        a.User = request.user
        a.NoAlarmTime = datetime.datetime.now()
        reson = 'NO RESON'
        try:
            reson = request.REQUEST['reson']
        except:
            pass

    a.NoAlarmReson = unquote(reson)
    a.save()
    return DEV_STATUS_ALARM


def reloadDataCmd(dObj):
    dObj.OpLogStamp = 0
    dObj.LogStamp = 0
    dObj.save()
    appendDevCmd(dObj, 'CHECK')


def reloadLogDataCmd(dObj):
    dObj.LogStamp = 0
    dObj.save()
    appendDevCmd(dObj, 'CHECK')


def resetPwd(dev, pin, pwd, cursor):
    if pin == '0':
        appendDevCmd(dev, 'RESET PWD PIN=%s\tPasswd=%s' % (1, pwd), cursor)
        appendDevCmd(dev, 'RESET PWD PIN=%s\tPasswd=%s' % (2, pwd), cursor)
    else:
        appendDevCmd(dev, 'RESET PWD PIN=%s\tPasswd=%s' % (pin, pwd), cursor)
    return cursor


def restoreData(dev, cursor):
    emps = employee.objects.filter(SN=dev).filter(DeptID__isnull=False)
    for emp in emps:
        appendEmpToDev(dev, emp, cursor, True)

    return cursor


def appendEmpToDev(dev, emp, cursor=None, onlyEnrollDev=False, cmdTime=None):
    bdev = None
    edev = emp.Device()
    if not onlyEnrollDev and edev and edev.SN == dev.SN:
        bdev = dev.BackupDevice()
    s = getEmpCmdStr(emp)
    appendDevCmd(dev, s, cursor, cmdTime)
    print '---------------appendDevCmd ------------------'
    now = datetime.datetime.now()
    filepath = os.path.abspath(os.path.dirname(sys.argv[0]))
    old_file = '%s\\UserToDev%s.txt' % (tmpDir(), now.strftime('%y%m%d')[:10])
    dt = str(datetime.datetime.now())[:10]
    f = file(old_file, 'w+b')
    f.write(s.encode('utf-8') + '\n')
    f.flush()
    f.close()
    if bdev:
        appendDevCmd(bdev, s, cursor, cmdTime)
    fps = fptemp.objects.filter(UserID=emp.id)
    for fp in fps:
        if fp.Template:
            try:
                s = u'DATA UPDATE FINGERTMP PIN=%s\tFID=%d\tSize=%s\tValid=1\tTMP=%s' % (
                    emp.pin(), fp.FingerID, len(fp.temp()), fp.temp())
                appendDevCmd(dev, s, cursor, cmdTime)
                if bdev:
                    appendDevCmd(bdev, s, cursor, cmdTime)
                f = file(old_file, 'w+b')
                f.write(s + '\n')
                f.flush()
                f.close()
            except:
                errorLog()

    return cursor


def appendEmpToDevWithin(dev, emp, startTime, endTime, cursor=None):
    pin = emp.pin()
    edev = emp.Device()
    if not edev or edev.SN != dev.SN:
        appendEmpToDev(dev, emp, cursor, False, startTime)
        if endTime and endTime.year > 2007:
            appendDevCmd(dev, 'DATA DELETE USERINFO PIN=%s' % pin, cursor, endTime)
    return cursor


def empLeave(emp):
    dev = emp.Device()
    emp.OffDuty = 1
    emp.save()
    pin = emp.pin()
    if dev:
        appendDevCmd(dev, 'DATA DELETE USERINFO PIN=%s' % pin)
        bdev = dev.BackupDevice()
        if bdev:
            appendDevCmd(bdev, 'DATA DELETE USERINFO PIN=%s' % pin)
            return
        return


def copyDevEmpToDev(ddev, sdev, cursor=None):
    ret = cursor
    if ddev.SN == sdev.SN:
        return ret
    emps = employee.objects.all().filter(SN=sdev).filter(DeptID__isnull=False)
    for e in emps:
        ret = appendEmpToDev(ddev, e, cursor)

    return ret


def devCheckData(dev):
    dev.LogStamp = 0
    dev.OpLogStamp = 0
    dev.save()
    appendDevCmd(dev, 'CHECK')


def changeEmpDept(dept, emp):
    emp.DeptID = dept
    emp.save()


def copyFromData(dataModel, obj, src, fields):
    for field in fields:
        obj.__setattr__(field, src.__getattribute__(field))

    obj.save()


def getFW(dev):
    ds = dev.DeviceName
    if not ds:
        ds = ''
    else:
        ds = ds + '/'
    return ('file/fw/%smain.gz' % ds, '%sfw/%smain.gz' % (settings.ADDITION_FILE_ROOT, ds))


def getU(dev):
    ds = dev.DeviceName
    if not ds:
        ds = ''
    else:
        ds = ds + '/'
    return ('file/fw/%semfw.cfg' % ds, '%sfw/%semfw.cfg' % (settings.ADDITION_FILE_ROOT, ds))


def getO(dev):
    ds = dev.DeviceName
    if not ds:
        ds = ''
    else:
        ds = ds + '/'
    return ('file/fw/%soption2.cfg' % ds, '%sfw/%soption2.cfg' % (settings.ADDITION_FILE_ROOT, ds))


def UpdateByU(dev):
    ds = dev.FWVersion
    if not ds:
        return _(u'The Firmware version of device %(object_name)s is unknown\uff0ccannot to be upgraded!') % {
            'object_name': dev}
    mainVer, timeVer = ds[:8], ds[9:]
    url, fname = getU(dev)
    if os.path.exists(fname):
        appendDevCmd(dev, 'PutFile %s\temfw.cfg' % url)
    else:
        return _(u"The firmware file '%(object_name)s' does not exist, can not upgrade firmware for %(esc_name)s!") % {
            'object_name': fname, 'esc_name': dev}
    url, fname = getO(dev)
    if os.path.exists(fname):
        appendDevCmd(dev, 'PutFile %s\toption2.cfg' % url)
    else:
        return _(u"The firmware file '%(object_name)s' does not exist, can not upgrade firmware for %(esc_name)s!") % {
            'object_name': fname, 'esc_name': dev}


def devUpdateFirmware(dev):
    ds = dev.FWVersion
    if not ds:
        return _(u'The Firmware version of device %(object_name)s is unknown\uff0ccannot to be upgraded!') % {
            'object_name': dev}
    mainVer, timeVer = ds[:8], ds[9:]
    url, fname = getFW(dev)
    if os.path.exists(fname):
        appendDevCmd(dev, 'PutFile %s\tmain.gz' % url)
        appendDevCmd(dev, 'REBOOT')
    else:
        return _(u"The firmware file '%(object_name)s' does not exist, can not upgrade firmware for %(esc_name)s!") % {
            'object_name': fname, 'esc_name': dev}


def rebootDevice(dev):
    if dev.getDynState() == DEV_STATUS_OK:
        appendDevCmd(dev, 'REBOOT')
    else:
        if dev.IPAddress:
            rebDevs([dev.IPAddress])


def clearDevData(dev):
    appendDevCmd(dev, 'CLEAR DATA')


def enrollAEmp(dev, emp):
    if not dev:
        dev = emp.Device()
    if not dev:
        return _(u'Not specified a device to enroll')
    fids = fptemp.objects.filter(UserID=emp).values_list('FingerID')
    for i in range(10):
        if (
                i,) not in fids:
            appendDevCmd(dev, 'ENROLL_FP PIN=%s\tFID=%d\tRETRY=%d\tOVERWRITE=0' % (int(emp.PIN), i, 3))
            return

    return _('All fingerprint have enrolled')
