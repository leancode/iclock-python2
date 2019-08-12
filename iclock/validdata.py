import string, os


def hashpjw(data):
    i, val = (0, 0)
    for ch in data:
        val = (val << 4) + ord(ch)
        tmp = val & 4026531840L
        if tmp > 2147483647:
            tmp = tmp - 4294967296L
        if tmp != 0:
            val = val ^ tmp >> 24
            val = val ^ tmp
        val = val & 4294967295L
        i += 1

    return val % 16711679


def checkALogData(data):
    if data[:3] != 'SN=':
        return (None, data, None)
    rawdata, checksum = data.split('CHECKSUM=', 1)
    checksum = int(checksum)
    if checksum < 0:
        checksum = 4294967296L + checksum
    sum = 0
    for line in rawdata.split('\r\n'):
        if line:
            sum = sum + hashpjw(line + '\r\n')

    sum = sum & 4294967295L
    if sum == checksum:
        sn, rawdata = rawdata.split('\r\n', 1)
        sn = sn[3:]
        return (
            sn, rawdata, sum)
    return (False, False, False)


def checkRecData(data, recSize):
    if data[:3] != 'SN=':
        return (None, data, None)
    rawdata, checksum = data.split('CHECKSUM=', 1)
    checksum = int(checksum)
    if checksum < 0:
        checksum = 4294967296L + checksum
    sn, rawdata = rawdata.split('\r\n', 1)
    sum = hashpjw(sn + '\r\n')
    if len(rawdata) % recSize != 0:
        return (False, False, False)
    for i in range(len(rawdata) / recSize):
        sum = sum + hashpjw(rawdata[i * recSize:(i + 1) * recSize])

    sum = sum & 4294967295L
    if sum == checksum:
        sn = sn[3:]
        return (
            sn, rawdata, sum)
    return (False, False, False)


def testHash():
    s = ('123\x00').ljust(15).replace(' ', '\xef')


if __name__ == '__main__':
    testHash()
    data = file('g:\\1_attlog.dat', 'rb').read()
