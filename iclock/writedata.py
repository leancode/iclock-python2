from django.conf import settings
from django.utils.encoding import smart_str

if settings.DATABASE_ENGINE == 'pool':
    settings.DATABASE_ENGINE = settings.POOL_DATABASE_ENGINE
from models import *
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
import string, datetime, time, os, re
from mysite.utils import *
from devview import lineToLog, getDevice
from devview import commitLog as cld
from devview import lineToUser
from django.db import IntegrityError
from traceback import print_exc
from mysite.settings import AutoDelTmp, AutoDelTmpDay

atts = transaction.objects.filter(State='I')
for a in atts:
    a.State = '0'
    a.save()

atts = transaction.objects.filter(State='O')
for a in atts:
    a.State = '1'
    a.save()


def commitLog(conn, cursor, sql):
    try:
        cld(cursor, sql, conn)
    except IntegrityError:
        pass
    except Exception, ex:
        raise ex
    except:
        print_exc()
        print 'try again'
        conn._rollback()
        conn.close()
        cursor = conn.cursor()
        cld(cursor, sql, conn)

    return cursor


def parseAOpLogData(device, conn, cursor, lines):
    print 'user or op lines count:', len(lines)
    c = 0
    ec = 0
    try:
        user = False
        for line in lines:
            try:
                if line:
                    user = lineToUser(cursor, device, line)
                    c = c + 1
            except Exception, e:
                ec = ec + 1
                appendFile('ERROR(cdata-writedata):%s\nLine:%s' % (e, line))

        try:
            conn._commit()
        except:
            print_exc()
        else:
            dlogObj = 'TMP'
            try:
                dlogObj = (u'%s' % user)[:20]
            except:
                pass

        devlog(SN=device, Cnt=c, OP=u'USERDATA', ECnt=ec, Object=dlogObj, OpTime=datetime.datetime.now()).save()
    except Exception, e:
        print_exc()

    return (c + ec, c)


def parseATransLogData(device, conn, cursor, lines):
    print 'trans lines count:', len(lines)
    okc = 0
    errorLogs = []
    errorLines = []
    cacheLines = []
    sqls = []
    lc = 0
    for l in lines:
        if not l:
            break
        lc += 1
        eMsg = ''
        alog = ''
        try:
            log = lineToLog(device, l)
        except Exception, e:
            eMsg = u'%s' % e
            errorLogs.append('%s\t--%s' % (l, eMsg))
            log = None
        else:
            if log:
                sqls.append(log)
                cacheLines.append(l)
                print 'len cache lines count : %s' % len(cacheLines)
                if len(cacheLines) >= 700:
                    try:
                        cursor = commitLog(conn, cursor, sqls)
                        okc += len(cacheLines)
                        print '\tcommit ', len(cacheLines)
                        alog = cacheLines[0]
                    except:
                        errorLines += cacheLines
                    else:
                        cacheLines = []
                        sqls = []

    if cacheLines:
        try:
            cursor = commitLog(conn, cursor, sqls)
            okc += len(cacheLines)
            print '\tcommit last:', len(cacheLines)
            if not alog:
                alog = cacheLines[0]
        except:
            print_exc()
            errorLines += cacheLines

    if errorLines:
        cacheLines = errorLines
        errorLines = []
        for line in cacheLines:
            if line not in errorLogs:
                try:
                    log = lineToLog(device, line)
                    cursor = commitLog(conn, cursor, log)
                    okc += 1
                    print '\tcommit last error:', line
                except Exception, e:
                    eMsg = u'%s' % e
                    if 'Duplicate' not in eMsg:
                        errorLines.append('%s\t--%s' % (line, eMsg))

    errorLines += errorLogs
    dlogObj = ''
    try:
        if okc == 1:
            dlogObj = alog
        else:
            if okc > 1:
                dlogObj = alog + ', ...'
    except Exception, e:
        eMsg = u'%s' % e
        errorLines.append('%s\t--%s' % (line, eMsg))
    else:
        log = devlog(SN_id=device.SN, Cnt=okc, ECnt=len(errorLines), Object=dlogObj[:20],
                     OpTime=datetime.datetime.now())
        try:
            log.save()
        except:
            try:
                device.save()
                log.save()
            except Exception, e:
                eMsg = u'%s' % e
                errorLines.append('%s\t--%s' % (line, eMsg))

        if errorLines:
            tmpFile('transaction_%s_%s.txt' % (device.SN, log.id), ('\n').join(errorLines))

    return (
        lc, okc)


def parseATransData(conn, cursor, lines):
    l = lines[0]
    try:
        sn = l.split('SN=')[1].split('\t')[0]
        device = getDevice(sn)
    except:
        device = None
    else:
        if device is None:
            print 'UNKOWN Device'
        if ':TRANSACTIONS:' in l:
            return parseATransLogData(device, conn, cursor, lines[1:])
        if ':OPLOG:' in l:
            return parseAOpLogData(device, conn, cursor, lines[1:])
        print 'UNKOWN DATA', lines

    return (len(lines), 0)


def parseLogDataInFile(conn, cursor):
    start_time = time.time()
    i = 0
    lc = 0
    tmp_dir = tmpDir()
    while True:
        if time.time() - start_time > 600:
            break
        fcount = 0
        files = os.listdir(tmp_dir + '\\read')
        for file_name in files:
            if file_name[-4:] == '.txt':
                tmp_file = '%s\\read\\%s' % (tmp_dir, file_name)
                print 'read data file: ', tmp_file
                try:
                    lines = file(tmp_file, 'rb').read()
                except Exception, e:
                    appendFile(e + 'step 1')
                    continue
                else:
                    if lines:
                        lcc, okc = parseATransData(conn, cursor, lines.splitlines())
                        lc += lcc
                        i += okc
                    now = datetime.datetime.now()
                    new_file = '%s\\write\\%s\\%s' % (tmp_dir, now.strftime('%Y%m%d'), file_name)
                    try:
                        os.renames(tmp_file, new_file)
                    except:
                        try:
                            os.remove(tmp_file)
                        except Exception, e:
                            appendFile(e)

                    else:
                        fcount += 1

        if fcount == 0:
            print 'no transactions in the directory'
            time.sleep(10)
        if lc > 50000:
            break

    print 'lines: %s, valid: %s, seconds: %s' % (lc, i, int(time.time() - start_time))
    return i


def parseLogDataInQueqe(conn, cursor, q_server):
    start_time = time.time()
    i = 0
    lc = 0
    while True:
        if time.time() - start_time > 600:
            break
        try:
            lines = q_server.rpop('TRANS')
        except Exception, e:
            time.sleep(1)
            continue
        else:
            if not lines:
                print 'no transactions in the queqe'
                time.sleep(5)
                continue
            if lines:
                lcc, okc = parseATransData(conn, cursor, lines.decode('utf-8').splitlines())
                lc += lcc
                i += okc
            if lc > 50000:
                break

    print 'lines: %s, valid: %s, seconds: %s' % (lc, i, int(time.time() - start_time))
    return i


def performPostDataFile_(count=10):
    wt = []
    for i in range(count):
        t = WriteDataThread(i)
        wt.append(t)
        t.start()
        time.sleep(1)

    while False:
        time.sleep(1)
        all_finished = True
        for t in wt:
            if t.isAlive():
                all_finished = False
                break

        if all_finished:
            break


def formatDate():
    now = datetime.datetime.now()
    ds = AutoDelTmpDay
    oldtime = now - datetime.timedelta(days=ds)
    return oldtime


def fmtCreatTime(yy, mm, dd):
    while len(yy) < 4:
        yy = '0' + yy

    while len(mm) < 2:
        mm = '0' + mm

    while len(dd) < 2:
        dd = '0' + dd

    return yy + mm + dd


def auto_del():
    tmp_dir = tmpDir()
    dir = '%s\\write\\' % tmp_dir
    type = 'txt'
    folders = os.listdir(dir)
    olddate = formatDate().strftime('%Y%m%d')
    rr = re.compile('\\.%s$' % type, re.I)
    for folder in folders:
        if folder == '0':
            continue
        if folder <= olddate:
            dirs = dir + folder + '\\'
            files = os.listdir(dirs)
            for f in files:
                if rr.search(f):
                    os.remove(dirs + f)

            os.rmdir(dirs)

    if AutoDelTmp:
        dir = '%s\\' % tmp_dir
        folders = os.listdir(dir)
        rr = re.compile('\\.%s$' % type, re.I)
        for folder in folders:
            if rr.search(folder):
                info = os.stat(dir + folder)
                ctime = time.localtime(info.st_ctime)
                creatTime = fmtCreatTime(str(ctime[0]), str(ctime[1]), str(ctime[2]))
                if creatTime <= olddate:
                    os.remove(dir + folder)

    return 'Auto Check&Delete succeed!(LastDate:%s)' % olddate


def run_writedata(index=0):
    from django.db import backend
    try:
        from django.db import connection
    except Exception, ee:
        print '--ee:', ee
    else:
        q = queqe_server()
        cursor = connection.cursor()
        print '-----------------------Start Writedata %s' % index
        if AutoDelTmp:
            try:
                ret = auto_del()
            except Exception, e:
                print '--Auto Check&Delete failed!(%s):' % e

        parseLogDataInFile(connection, cursor)
        try:
            cursor.close()
            connection.close()
        except:
            pass

    q.connection.disconnect()
    print '-----------------------End Writedata %s' % index


class WriteDataThread(threading.Thread):

    def __init__(self, index):
        self.index = index
        super(WriteDataThread, self).__init__()

    def run(self):
        run_writedata(self.index)


def performPostDataFile(count=10):
    run_writedata(0)
