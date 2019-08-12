from mysite.iclock.models import *
import string, datetime, time


def readTransFrom(UserID, startTime):
    return transaction.objects.filter(UserID=UserID, TTime__gte=startTime).order_by('TTime').values('TTime', 'SN')


invalid_pins = []


def transASch(line):
    s = line.split('\t')
    pin = s[0]
    if pin in invalid_pins:
        return
    try:
        sch = {'UserID': employee.objByPIN(pin, None).id, 'PIN': pin}
    except:
        invalid_pins.append(pin)
        return
    else:
        startDate = s[1]
        sch['Date'] = datetime.datetime.strptime(startDate, '%Y%m%d')
        sch['Start'] = datetime.datetime.strptime(startDate + s[2], '%Y%m%d%H%M%S')
        endTime = datetime.datetime.strptime(startDate + s[3][:6], '%Y%m%d%H%M%S')
        if sch['Start'] == endTime:
            return
        if endTime < sch['Start']:
            sch['End'] = endTime + datetime.timedelta(1)
        sch['End'] = endTime

    return sch


def cmpSch(s1, s2):
    u1 = s1['UserID']
    u2 = s2['UserID']
    if u1 < u2:
        return -1
    if u1 > u2:
        return 1
    t1 = s1['Date']
    t2 = s2['Date']
    if t1 < t2:
        return -1
    if t1 > t2:
        return 1
    t1 = s1['Start']
    t2 = s2['Start']
    if t1 < t2:
        return -1
    if t1 > t2:
        return 1
    return 0


def readSchedule(schFile):
    fileData = file(schFile, 'rb').read()
    schs = []
    for line in fileData.split('\n'):
        try:
            if line:
                sch = transASch(line)
                if sch:
                    schs.append(sch)
        except Exception, e:
            print 'LINE  :', line
            print 'ERROR :', e.message

    schs.sort(cmpSch)
    return schs


CHECK_IN = True
CHECK_OUT = False


def writeATran(f, pin, ttime, devSN, stateIn=CHECK_IN):
    st = ttime.strftime('%Y%m%d%H%M%S')
    ssn = ('0000' + (devSN or ''))[-4:]
    s = '%s%s%s%s%s10000010\r\n' % (
        stateIn and 'P10' or 'P20',
        ssn, st, st, pin)
    f.write(s)


def writeATranInOut(f, sch, pin):
    if 'Saved' in sch:
        return
    if 'In' in sch:
        writeATran(f, pin, sch['In']['TTime'], sch['In']['SN'], CHECK_IN)
    if 'Out' in sch:
        writeATran(f, pin, sch['Out']['TTime'], sch['Out']['SN'], CHECK_OUT)
    sch['Saved'] = True


def outALine(s):
    pass


def adjustState(t, sch, p0, p1, p2, log):
    if 'In' not in sch:
        if 'Out' not in sch:
            if t < p2:
                sch['In'] = log
                outALine('In : %s' % log['TTime'])
            else:
                sch['Out'] = log
                outALine('Out: %s' % log['TTime'])
            return
        t2 = sch['Out']['TTime']
        if (t - t2).seconds >= 3600:
            sch['In'] = sch['Out']
            sch['Out'] = log
            outALine('In-: %s' % sch['In']['TTime'])
            outALine('Out: %s' % log['TTime'])
            return
        sch['Out'] = log
        outALine('Out: %s' % log['TTime'])
        return
    t2 = sch['In']['TTime']
    if (t - t2).seconds >= 3600:
        sch['Out'] = log
        outALine('Out: %s' % log['TTime'])
        return
    outALine('!!!: %s' % log['TTime'])


def writeTransState(f, logs, schs, lastEmp):
    if not logs:
        return
    if not schs:
        return
    pin = schs[0]['PIN']
    schi = 0
    schl = len(schs)
    sch = schs[schi]
    sp0 = sch['Start'] - datetime.timedelta(0, 14400)
    sp1 = sp0 + datetime.timedelta(1)
    sp2 = sch['Start'] + datetime.timedelta(0, 10800)
    for log in logs:
        t = log['TTime']
        if t < sp0:
            pass
        else:
            if t >= sp1:
                writeATranInOut(f, sch, pin)
                schi += 1
                while schi < schl:
                    sch = schs[schi]
                    sp0 = sch['Start'] - datetime.timedelta(0, 14400)
                    sp1 = sp0 + datetime.timedelta(1)
                    sp2 = sch['Start'] + datetime.timedelta(0, 10800)
                    if t < sp1:
                        break
                    schi += 1

                if t >= sp1:
                    break
            adjustState(t, sch, sp0, sp1, sp2, log)

    writeATranInOut(f, sch, pin)


def outLogs(logs):
    return
    for l in logs:
        print '%s' % l['TTime']


def parseTransState(schFile, fileName='l.txt'):
    schs = readSchedule(schFile)
    if not schs:
        return
    f = file(fileName, 'w+b')
    lastEmp = ''
    logs = []
    lastSchs = []
    for sch in schs:
        emp = sch['UserID']
        if emp != lastEmp:
            if lastEmp != '':
                writeTransState(f, logs, lastSchs, lastEmp)
            logs = readTransFrom(emp, sch['Date'] - datetime.timedelta(1))
            outLogs(logs)
            lastEmp = emp
            lastSchs = []
        lastSchs.append(sch)

    if lastSchs:
        writeTransState(f, logs, lastSchs, lastEmp)
    f.close()
