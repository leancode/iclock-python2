staticfiles.py
"""
Views and functions for serving static files. These are only to be used
during development, and SHOULD NOT be used in a production setting.
"""
import mimetypes, os, posixpath, re, stat, urllib
from email.Utils import parsedate_tz, mktime_tz
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.template import Template, Context, TemplateDoesNotExist
from django.utils.http import http_date


def serve(request, path, document_root=None, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.
    
    To use, put a URL pattern such as::
    
        (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'})
    
    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index``.
    """
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')

    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(newpath, fullpath)
        raise Http404, 'Directory indexes are not allowed here.'
    if not os.path.exists(fullpath):
        raise Http404, '"%s" does not exist' % fullpath
    statobj = os.stat(fullpath)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), statobj[stat.ST_MTIME],
                              statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    contents = open(fullpath, 'rb').read()
    if request.META.get('RANGE'):
        start, end = request.META.get('RANGE').split('bytes=')[1].split('-')
        contents = contents[start:end + 1]
        response = HttpResponse(contents, mimetype=mimetype, status=206)
        response['Content-Range'] = '%s/%d' % (request.META.get('RANGE'), end - start + 1)
    else:
        response = HttpResponse(contents, mimetype=mimetype)
    response['Last-Modified'] = http_date(statobj[stat.ST_MTIME])
    response['Content-Length'] = len(contents)
    response['Accept-Ranges'] = 'bytes'
    return response


DEFAULT_DIRECTORY_INDEX_TEMPLATE = '\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n  <head>\n    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n    <meta http-equiv="Content-Language" content="en-us" />\n    <meta name="robots" content="NONE,NOARCHIVE" />\n    <title>Index of {{ directory|escape }}</title>\n  </head>\n  <body>\n    <h1>Index of {{ directory|escape }}</h1>\n    <ul>\n      {% for f in file_list %}\n      <li><a href="{{ f|urlencode }}">{{ f|escape }}</a></li>\n      {% endfor %}\n    </ul>\n  </body>\n</html>\n'


def directory_index(path, fullpath):
    try:
        t = loader.get_template('static/directory_index')
    except TemplateDoesNotExist:
        t = Template(DEFAULT_DIRECTORY_INDEX_TEMPLATE, name='Default directory index template')
    else:
        files = []
        for f in os.listdir(fullpath):
            if not f.startswith('.'):
                if os.path.isdir(os.path.join(fullpath, f)):
                    f += '/'
                files.append(f)

    c = Context({'directory': path + '/',
                 'file_list': files})
    return HttpResponse(t.render(c))


def was_modified_since(header=None, mtime=0, size=0):
    """
    Was something modified since the user last downloaded it?
    
    header
      This is the value of the If-Modified-Since header.  If this is None,
      I'll just return True.
    
    mtime
      This is the modification time of the item we're talking about.
    
    size
      This is the size of the item we're talking about.
    """
    try:
        if header is None:
            raise ValueError
        matches = re.match('^([^;]+)(; length=([0-9]+))?$', header, re.IGNORECASE)
        header_mtime = mktime_tz(parsedate_tz(matches.group(1)))
        header_len = matches.group(3)
        if header_len and int(header_len) != size:
            raise ValueError
        if mtime > header_mtime:
            raise ValueError
    except (AttributeError, ValueError):
        return True

    return False
