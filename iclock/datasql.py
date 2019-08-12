from django.utils.translation import ugettext as _
from django.http import QueryDict, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render_to_response


def sql_page(request):
    sql = str(request.POST.get('sql', '')).strip()
    get_content = u'\n\t\t<br /><br /><br />\n\t\t<form id="form1" action="" method="POST">\n\t\t<div style="margin-left:100px;">\n\t\t\t<input type="text" name="sql" value="%s" size="120" />\n\t\t\t<input type="submit" name="submit" value="\u6267\u884c SQL \u8bed\u53e5" />\n\t\t</div>\n\t\t</form>\t<hr /><br />\n\t\t' % sql
    if sql:
        from django.db import connection as conn
        cursor = conn.cursor()
        try:
            count = 50
            if sql.startswith('select') or sql.startswith('SELECT') or sql.startswith('count='):
                if sql.startswith('count='):
                    pos = sql.index(' ')
                    count = int(sql[6:pos])
                    sql = sql[pos + 1:]
                cursor.execute(sql)
                conn._commit()
                i, rs = (0, '')
                while i < count:
                    rs_one = cursor.fetchone()
                    if rs_one is None:
                        break
                    rs += u"<tr><td style='color:red;'>%d</td>" % (i + 1)
                    for row in rs_one:
                        try:
                            rs += u'<td>%s</td>' % (row and row or '&nbsp')
                        except:
                            rs += u'<td>[E]</td>'

                    rs += u'</tr>'
                    i += 1

                rs = u'<table border="1">%s</table>' % rs
                return HttpResponse(u'%s<h2>\u6267\u884c %s \u6210\u529f</h2><br />%s' % (get_content, str(sql), rs))
            cursor.execute(sql)
            conn._commit()
            return HttpResponse(u'%s\u6267\u884c %s \u6210\u529f' % (get_content, str(sql)))
        except Exception, args:
            return HttpResponse(u'%s<h2>\u6267\u884c %s \u5931\u8d25</h2><br /><br />%s' % (
                get_content, str(sql), str(Exception) + str(args)))

    return HttpResponse(get_content)
