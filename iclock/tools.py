def getSQL_insert(table, **kwargs):
    """
		Generate an insert SQL statement
    """
    ks = ''
    vs = ''
    for k, v in kwargs.items():
        ks += k + ','
        if isNumber(v) or v == 'null':
            vs += str(v) + ','
        else:
            vs += "'" + v + "',"

    return 'INSERT INTO %s (%s) VALUES (%s)' % (table, ks[:-1], vs[:-1])


def getSQL_update(table, **kwargs):
    """ 
		Generate update SQL statement
    """
    kvs = ''
    kvs_where = ''
    for k, v in kwargs.items():
        if k.startswith('where'):
            kvs_where += k[5:] + '='
            if isNumber(v) or v == 'null':
                kvs_where += str(v) + ' and '
            else:
                kvs_where += "'" + v + "' and "
        else:
            if not v:
                continue
            if isNumber(v) or v == 'null':
                kvs += k + '=' + str(v) + ','
            else:
                kvs += k + "='" + v + "',"

    if kvs_where == '':
        return 'UPDATE %s SET %s' % (table, kvs[:-1])
    return 'UPDATE %s SET %s WHERE %s' % (table, kvs[:-1], kvs_where[:-4])


def getSQL_update_ex(table, dict):
    """
		Generate update SQL statement
    """
    kvs = ''
    kvs_where = ''
    for k, v in dict.items():
        if k.startswith('where'):
            kvs_where += k[5:] + '='
            if isNumber(v) or v == 'null':
                kvs_where += str(v) + ' and '
            else:
                kvs_where += "'" + v + "' and "
        else:
            if not v:
                continue
            if isNumber(v) or v == 'null':
                kvs += k + '=' + str(v) + ','
            else:
                kvs += k + "='" + v + "',"

    if kvs_where == '':
        return 'UPDATE %s SET %s' % (table, kvs[:-1])
    return 'UPDATE %s SET %s WHERE %s' % (table, kvs[:-1], kvs_where[:-4])


def isNumber(num):
    """
		Determine whether the number (int float long)
    """
    try:
        abs(num)
        return True
    except:
        return False


def getStr_c(s):
    """
		Get the string of data transmitted by the C language system
    """
    try:
        return s[:s.index('\x00')]
    except:
        return s


def getFptemp_c(s):
    """ 
		Get the fingerprint template transmitted from the C language system (filled behind)
    """
    i = len(s) - 1
    while i > 0 and s[i] == '\x00':
        i -= 1

    return s[:i]


def getStr_c_decode(s):
    """
		Get the string of data transmitted by the C language system and decode it by gb18030
    """
    try:
        return unicode(s[:s.index('\x00')].decode('gb18030'))
    except:
        return unicode(s.decode('gb18030'))


def getSQL_insert_ex(table, dict):
    """ 
		Generate an insert SQL statement
    """
    ks = ''
    vs = ''
    for k, v in dict.items():
        ks += k + ','
        if v == None:
            v = 'null'
        if isNumber(v) or v == 'null':
            vs += str(v) + ','
        elif str(type(v)) == "<type 'datetime.datetime'>":
            vs += "'" + v.strftime('%Y-%m-%d %H:%M:%S') + "',"
        elif str(type(v)) == "<type 'datetime.time'>":
            vs += "'" + v.strftime('%H:%M:%S') + "',"
        else:
            vs += "'" + v + "',"

    return 'INSERT INTO %s (%s) VALUES (%s)' % (table, ks[:-1], vs[:-1])
