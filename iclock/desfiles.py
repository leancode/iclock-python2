from mysite.iclock.models import *
from mysite.iclock.tools import *
import string, os, datetime, time
from mysite.utils import *
from mysite.iclock.iutils import *
from django.utils.translation import ugettext_lazy as _

spLine = '====================================='


def desSSRUser(upload_user):
    emps = [
        u'PIN,Name', spLine]
    i, count = 0, len(upload_user) / 72
    if not (count > 0 and count * 72 == len(upload_user)):
        raise Exception()
    i_insert, i_update, i_rep = (0, 0, 0)
    while i < count:
        buf = upload_user[i * 72:(i + 1) * 72]
        pin = ord(buf[0]) + ord(buf[1]) * 256
        if pin:
            pin = formatPIN(getStr_c_decode(buf[48:]))
            ename = getStr_c_decode(buf[11:35])
            Password = getStr_c_decode(buf[3:11])
            emps.append(u'%s,%s' % (pin, ename))
        i += 1

    emps.append(spLine)
    emps.append(u'total %d' % i)
    return (u'\r\n').join(emps)


def desSSRAttLog(data):
    emps = [
        u'PIN,Time,Verification,State', spLine]
    i, count = 0, len(data) / 40
    if not (count > 0 and count * 40 == len(data)):
        raise Exception()
    i_insert, i_update, i_rep = (0, 0, 0)
    while i < count:
        buf = data[i * 40:(i + 1) * 40]
        pin = formatPIN(getStr_c_decode(buf[2:26]))
        timeStr = decodeTime(buf[27:31])
        verify = ord(buf[26])
        status = ord(buf[31])
        emps.append(u'%s,%s,%s,%s' % (pin, timeStr, verify, status))
        i += 1

    emps.append(spLine)
    emps.append(_('%d attendance record(s).') % i)
    return (u'\r\n').join(emps)


def desOpLog(data):
    recSize = 16
    emps = [u'Administarator, Time, Operation, Objects(1,2,3,4)', spLine]
    i, count = 0, len(data) / recSize
    if not (count > 0 and count * recSize == len(data)):
        raise Exception()
    while i < count:
        buf = data[i * recSize:(i + 1) * recSize]
        pin = ord(buf[0]) + ord(buf[1]) * 256
        op = OpName(ord(buf[2]))
        timeStr = decodeTime(buf[4:8])
        emps.append(u'%s, %s, %s, [%s,%s,%s,%s]' % (pin, timeStr, op,
                                                    ord(buf[8]) + ord(buf[9]) * 256, ord(buf[10]) + ord(buf[11]) * 256,
                                                    ord(buf[12]) + ord(buf[13]) * 256,
                                                    ord(buf[14]) + ord(buf[15]) * 256))
        i += 1

    emps.append(spLine)
    emps.append(u'Total %d' % i)
    return (u'\r\n').join(emps)
