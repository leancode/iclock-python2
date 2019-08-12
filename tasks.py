import os, sys
from mysite.utils import scheduleTask
from mysite.iclock.importwm import *

WORK_PATH = os.path.split(os.path.abspath(__file__))[0]
WORK_PATH = os.path.split(WORK_PATH)[0]


def hourlyTask():
    import datetime
    try:
        checkUpload()
    except:
        pass

    cmd = '%s\\hourlyTask.cmd %s' % (WORK_PATH, WORK_PATH)
    d = datetime.datetime.now() + datetime.timedelta(0, 3600)
    scheduleTask(cmd, d.strftime('%H:%M:%S'), [])


def dailyTask():
    checkEmpFile()


def weeklyTask():
    checkSchFile()


def installTasks():
    cmd = '%s\\dailyTask.cmd %s' % (WORK_PATH, WORK_PATH)
    scheduleTask(cmd, '00:00')
    cmd = '%s\\weeklyTask.cmd %s' % (WORK_PATH, WORK_PATH)
    scheduleTask(cmd, '00:00', ['Su,'])
    d = datetime.datetime.now() + datetime.timedelta(0, 3600)
    cmd = '%s\\hourlyTask.cmd %s' % (WORK_PATH, WORK_PATH)
    scheduleTask(cmd, d.strftime('%H:00'), [])


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc <= 1:
        hourlyTask()
    elif sys.argv[1] == 'daily':
        dailyTask()
    elif sys.argv[1] == 'week':
        weeklyTask()
    elif sys.argv[1] == 'install':
        installTasks()
    else:
        print 'ERROR argument'
