from django.template import Context, RequestContext, Template, TemplateDoesNotExist
from mysite.iclock.models import getUploadFileName, getUploadFileURL
from mysite.cab import listFile
import os
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from mysite.iclock.models import createThumbnail, formatPIN
from django.contrib.auth.decorators import login_required, permission_required
from mysite.iclock.iutils import userIClockList


def listPic(path, pattern):
    tnPath = os.path.split(getUploadFileName('thumbnail/' + path, '', ''))[0]
    picPath = os.path.split(getUploadFileName(path, '', ''))[0]
    flist = listFile(picPath, pattern)
    flist.sort()
    if not flist:
        return
    url = getUploadFileURL(path, '', '')
    List = []
    for f in flist:
        fname = os.path.split(f)[1]
        tname = tnPath + '/' + fname
        if not os.path.exists(tname):
            createThumbnail(f, tname)
        if 'fpimage' in path:
            name = fname.split('_')[1]
            fs = []
        else:
            fs = fname[:-4].split('_')
            name = fs[0]
            name = '%s:%s:%s' % (name[:2], name[2:4], name[4:])
        if len(fs) >= 2:
            name = (
                name, formatPIN(fs[1]))
        else:
            name = (
                name, None)
        item = (
            name, getUploadFileURL('thumbnail/' + path, '', fname),
            url + fname)
        List.append(item)

    return List


def listDir(request, path):
    sn_list = None
    valid_sn = None
    if not request.user.is_superuser:
        sn_list = userIClockList(request.user)
    if not path[0]:
        valid_sn = sn_list
    else:
        if sn_list != None and path[0] not in sn_list:
            return []
    path = ('/').join(path)
    path = getUploadFileName(path, '', '')
    for root, dirs, files in os.walk(path):
        if 'thumbnail' in dirs:
            dirs.remove('thumbnail')
        if valid_sn == None:
            return dirs
        return [i for i in dirs if i in valid_sn]

    return []


@login_required
def index(request, path):
    request.user.iclock_url_rel = ('../' * len(path.split('/')))[:-1]
    if path and path[-1] == '/':
        path = path[:-1]
    spath = path.split('/')
    if len(spath) <= 2:
        request.pic_flag = False
        fList = listDir(request, spath)
        if not fList:
            request.pic_flag = True
        return render_to_response('dirlist.html', RequestContext(request, {'title': path,
                                                                           'dirs': fList}))
    fList = listPic(path, ['*.jpg', '*.bmp'])
    return render_to_response('fpimage' in path and 'fppiclist.html' or 'piclist.html',
                              RequestContext(request, {'title': path,
                                                       'iclock_url_rel': request.user.iclock_url_rel,
                                                       'files': fList}))
