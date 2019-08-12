import urllib, datetime, os
from sgmllib import SGMLParser
from django.conf import settings
from mysite.iclock.models import iclock, devcmds
from mysite.utils import errorLog
from mysite.iclock.dataproc import appendDevCmd

citys = {u'\u5317\u4eac': u'54511',
         u'\u4e0a\u6d77': u'58367',
         u'\u5929\u6d25': u'54517',
         u'\u91cd\u5e86': u'57516',
         u'\u9999\u6e2f': u'45005',
         u'\u6fb3\u95e8': u'45011',
         u'\u54c8\u5c14\u6ee8': u'50953',
         u'\u9f50\u9f50\u54c8\u5c14': u'50745',
         u'\u7261\u4e39\u6c5f': u'54094',
         u'\u5927\u5e86': u'50842',
         u'\u4f0a\u6625': u'50774',
         u'\u53cc\u9e2d\u5c71': u'50884',
         u'\u9e64\u5c97': u'50775',
         u'\u9e21\u897f': u'50978',
         u'\u4f73\u6728\u65af': u'50873',
         u'\u4e03\u53f0\u6cb3': u'50971',
         u'\u9ed1\u6cb3': u'50468',
         u'\u7ee5\u5316': u'50853',
         u'\u5927\u5174\u5b89\u5cad': u'50442',
         u'\u957f\u6625': u'54161',
         u'\u5ef6\u8fb9': u'99999',
         u'\u5409\u6797': u'54172',
         u'\u767d\u5c71': u'54371',
         u'\u767d\u57ce': u'50936',
         u'\u56db\u5e73': u'54157',
         u'\u677e\u539f': u'50946',
         u'\u8fbd\u6e90': u'54260',
         u'\u5927\u5b89': u'50945',
         u'\u901a\u5316': u'54363',
         u'\u6c88\u9633': u'54342',
         u'\u5927\u8fde': u'54662',
         u'\u846b\u82a6\u5c9b': u'54453',
         u'\u65c5\u987a': u'54660',
         u'\u672c\u6eaa': u'54346',
         u'\u629a\u987a': u'54353',
         u'\u94c1\u5cad': u'54249',
         u'\u8fbd\u9633': u'54347',
         u'\u8425\u53e3': u'54471',
         u'\u961c\u65b0': u'54237',
         u'\u671d\u9633': u'54324',
         u'\u9526\u5dde': u'54337',
         u'\u4e39\u4e1c': u'54497',
         u'\u978d\u5c71': u'54339',
         u'\u547c\u548c\u6d69\u7279': u'53463',
         u'\u547c\u4f26\u8d1d\u5c14': u'99999',
         u'\u5305\u5934': u'53446',
         u'\u8d64\u5cf0': u'54218',
         u'\u6d77\u62c9\u5c14': u'50527',
         u'\u4e4c\u6d77': u'53512',
         u'\u9102\u5c14\u591a\u65af': u'53543',
         u'\u9521\u6797\u6d69\u7279': u'54102',
         u'\u901a\u8fbd': u'54135',
         u'\u77f3\u5bb6\u5e84': u'53698',
         u'\u5510\u5c71': u'54534',
         u'\u5f20\u5bb6\u53e3': u'54401',
         u'\u5eca\u574a': u'54515',
         u'\u90a2\u53f0': u'53798',
         u'\u90af\u90f8': u'53892',
         u'\u6ca7\u5dde': u'54616',
         u'\u8861\u6c34': u'54702',
         u'\u627f\u5fb7': u'54423',
         u'\u4fdd\u5b9a': u'54602',
         u'\u79e6\u7687\u5c9b': u'54449',
         u'\u90d1\u5dde': u'57083',
         u'\u5f00\u5c01': u'57091',
         u'\u6d1b\u9633': u'57073',
         u'\u5e73\u9876\u5c71': u'57171',
         u'\u7126\u4f5c': u'53982',
         u'\u9e64\u58c1': u'53990',
         u'\u65b0\u4e61': u'53986',
         u'\u5b89\u9633': u'53898',
         u'\u6fee\u9633': u'54900',
         u'\u8bb8\u660c': u'57089',
         u'\u6f2f\u6cb3': u'57186',
         u'\u4e09\u95e8\u5ce1': u'57051',
         u'\u5357\u9633': u'57178',
         u'\u5546\u4e18': u'58005',
         u'\u4fe1\u9633': u'57297',
         u'\u5468\u53e3': u'57195',
         u'\u9a7b\u9a6c\u5e97': u'57290',
         u'\u6d4e\u5357': u'54823',
         u'\u9752\u5c9b': u'54857',
         u'\u6dc4\u535a': u'54830',
         u'\u5a01\u6d77': u'54774',
         u'\u66f2\u961c': u'54918',
         u'\u4e34\u6c82': u'54938',
         u'\u70df\u53f0': u'54765',
         u'\u67a3\u5e84': u'58024',
         u'\u804a\u57ce': u'54806',
         u'\u6d4e\u5b81': u'54915',
         u'\u83cf\u6cfd': u'54906',
         u'\u6cf0\u5b89': u'54827',
         u'\u65e5\u7167': u'54945',
         u'\u4e1c\u8425': u'54736',
         u'\u5fb7\u5dde': u'54714',
         u'\u6ee8\u5dde': u'54734',
         u'\u83b1\u829c': u'54828',
         u'\u6f4d\u574a': u'54843',
         u'\u592a\u539f': u'53772',
         u'\u9633\u6cc9': u'53782',
         u'\u664b\u57ce': u'53976',
         u'\u664b\u4e2d': u'53778',
         u'\u4e34\u6c7e': u'53868',
         u'\u8fd0\u57ce': u'53959',
         u'\u957f\u6cbb': u'53882',
         u'\u6714\u5dde': u'53578',
         u'\u5ffb\u5dde': u'53674',
         u'\u5927\u540c': u'53487',
         u'\u5357\u4eac': u'58238',
         u'\u82cf\u5dde': u'58357',
         u'\u6606\u5c71': u'58356',
         u'\u5357\u901a': u'58259',
         u'\u592a\u4ed3': u'58377',
         u'\u5434\u53bf': u'58349',
         u'\u5f90\u5dde': u'58027',
         u'\u5b9c\u5174': u'58346',
         u'\u9547\u6c5f': u'58248',
         u'\u6dee\u5b89': u'58145',
         u'\u5e38\u719f': u'58352',
         u'\u76d0\u57ce': u'58151',
         u'\u6cf0\u5dde': u'58246',
         u'\u65e0\u9521': u'58354',
         u'\u8fde\u4e91\u6e2f': u'58044',
         u'\u626c\u5dde': u'58245',
         u'\u5e38\u5dde': u'58343',
         u'\u5bbf\u8fc1': u'58131',
         u'\u5408\u80a5': u'58321',
         u'\u5de2\u6e56': u'58326',
         u'\u868c\u57e0': u'58221',
         u'\u5b89\u5e86': u'58424',
         u'\u516d\u5b89': u'58311',
         u'\u6ec1\u5dde': u'58236',
         u'\u9a6c\u978d\u5c71': u'58336',
         u'\u961c\u9633': u'58203',
         u'\u5ba3\u57ce': u'58433',
         u'\u94dc\u9675': u'58429',
         u'\u6dee\u5317': u'58116',
         u'\u829c\u6e56': u'58334',
         u'\u6beb\u5dde': u'99999',
         u'\u5bbf\u5dde': u'58122',
         u'\u6dee\u5357': u'58224',
         u'\u6c60\u5dde': u'58427',
         u'\u897f\u5b89': u'57036',
         u'\u97e9\u57ce': u'53955',
         u'\u5b89\u5eb7': u'57245',
         u'\u6c49\u4e2d': u'57127',
         u'\u5b9d\u9e21': u'57016',
         u'\u54b8\u9633': u'57048',
         u'\u6986\u6797': u'53646',
         u'\u6e2d\u5357': u'57045',
         u'\u5546\u6d1b': u'57143',
         u'\u94dc\u5ddd': u'53947',
         u'\u5ef6\u5b89': u'53845',
         u'\u94f6\u5ddd': u'53614',
         u'\u56fa\u539f': u'53817',
         u'\u4e2d\u536b': u'53704',
         u'\u77f3\u5634\u5c71': u'53518',
         u'\u5434\u5fe0': u'53612',
         u'\u5170\u5dde': u'52889',
         u'\u767d\u94f6': u'52896',
         u'\u5e86\u9633': u'53829',
         u'\u9152\u6cc9': u'52533',
         u'\u5929\u6c34': u'57006',
         u'\u6b66\u5a01': u'52679',
         u'\u5f20\u6396': u'52652',
         u'\u7518\u5357': u'50741',
         u'\u4e34\u590f': u'52984',
         u'\u5e73\u51c9': u'53915',
         u'\u5b9a\u897f': u'52995',
         u'\u91d1\u660c': u'52675',
         u'\u897f\u5b81': u'52866',
         u'\u6d77\u5317': u'52754',
         u'\u6d77\u897f': u'52737',
         u'\u9ec4\u5357': u'56065',
         u'\u679c\u6d1b': u'56043',
         u'\u7389\u6811': u'56029',
         u'\u6d77\u4e1c': u'52875',
         u'\u6d77\u5357': u'52856',
         u'\u6b66\u6c49': u'57494',
         u'\u5b9c\u660c': u'57461',
         u'\u9ec4\u5188': u'57498',
         u'\u6069\u65bd': u'57447',
         u'\u8346\u5dde': u'57476',
         u'\u795e\u519c\u67b6': u'57362',
         u'\u5341\u5830': u'57256',
         u'\u54b8\u5b81': u'57590',
         u'\u8944\u6a0a': u'57278',
         u'\u5b5d\u611f': u'57482',
         u'\u968f\u5dde': u'57381',
         u'\u9ec4\u77f3': u'58407',
         u'\u8346\u95e8': u'57377',
         u'\u9102\u5dde': u'57496',
         u'\u957f\u6c99': u'57687',
         u'\u90b5\u9633': u'57766',
         u'\u5e38\u5fb7': u'57662',
         u'\u90f4\u5dde': u'57972',
         u'\u5409\u9996': u'57649',
         u'\u682a\u6d32': u'57780',
         u'\u5a04\u5e95': u'57763',
         u'\u6e58\u6f6d': u'57773',
         u'\u76ca\u9633': u'99999',
         u'\u6c38\u5dde': u'57866',
         u'\u5cb3\u9633': u'57584',
         u'\u8861\u9633': u'57872',
         u'\u6000\u5316': u'57749',
         u'\u97f6\u5c71': u'57771',
         u'\u5f20\u5bb6\u754c': u'57558',
         u'\u676d\u5dde': u'58457',
         u'\u6e56\u5dde': u'58450',
         u'\u91d1\u534e': u'58549',
         u'\u5b81\u6ce2': u'58563',
         u'\u4e3d\u6c34': u'58646',
         u'\u7ecd\u5174': u'58453',
         u'\u96c1\u8361\u5c71': u'99999',
         u'\u8862\u5dde': u'58633',
         u'\u5609\u5174': u'58452',
         u'\u53f0\u5dde': u'58660',
         u'\u821f\u5c71': u'58477',
         u'\u6e29\u5dde': u'58659',
         u'\u5357\u660c': u'58606',
         u'\u840d\u4e61': u'57786',
         u'\u4e5d\u6c5f': u'58502',
         u'\u4e0a\u9976': u'58637',
         u'\u629a\u5dde': u'58617',
         u'\u5409\u5b89': u'57799',
         u'\u9e70\u6f6d': u'58627',
         u'\u5b9c\u6625': u'57793',
         u'\u65b0\u4f59': u'57796',
         u'\u666f\u5fb7\u9547': u'58527',
         u'\u8d63\u5dde': u'57993',
         u'\u798f\u5dde': u'58847',
         u'\u53a6\u95e8': u'59134',
         u'\u9f99\u5ca9': u'58927',
         u'\u5357\u5e73': u'58834',
         u'\u5b81\u5fb7': u'58846',
         u'\u8386\u7530': u'58946',
         u'\u6cc9\u5dde': u'59137',
         u'\u4e09\u660e': u'58828',
         u'\u6f33\u5dde': u'59126',
         u'\u8d35\u9633': u'57816',
         u'\u5b89\u987a': u'57806',
         u'\u8d64\u6c34': u'57609',
         u'\u9075\u4e49': u'57713',
         u'\u94dc\u4ec1': u'57741',
         u'\u516d\u76d8\u6c34': u'56693',
         u'\u6bd5\u8282': u'57707',
         u'\u51ef\u91cc': u'57825',
         u'\u90fd\u5300': u'57827',
         u'\u6210\u90fd': u'56294',
         u'\u6cf8\u5dde': u'57602',
         u'\u5185\u6c5f': u'57504',
         u'\u51c9\u5c71': u'56571',
         u'\u963f\u575d': u'56171',
         u'\u5df4\u4e2d': u'57313',
         u'\u5e7f\u5143': u'57206',
         u'\u4e50\u5c71': u'56386',
         u'\u7ef5\u9633': u'56196',
         u'\u5fb7\u9633': u'56198',
         u'\u6500\u679d\u82b1': u'56666',
         u'\u96c5\u5b89 ': u'56287',
         u'\u5b9c\u5bbe': u'56492',
         u'\u81ea\u8d21': u'56396',
         u'\u7518\u5b5c\u5dde': u'56146',
         u'\u8fbe\u5dde': u'57328',
         u'\u8d44\u9633': u'56298',
         u'\u5e7f\u5b89': u'57415',
         u'\u9042\u5b81': u'57405',
         u'\u7709\u5c71': u'56391',
         u'\u5357\u5145': u'57411',
         u'\u5e7f\u5dde': u'59287',
         u'\u6df1\u5733': u'59493',
         u'\u6f6e\u5dde': u'59312',
         u'\u97f6\u5173': u'59082',
         u'\u6e5b\u6c5f': u'59658',
         u'\u60e0\u5dde': u'59298',
         u'\u6e05\u8fdc': u'59280',
         u'\u4e1c\u839e': u'59289',
         u'\u6c5f\u95e8': u'59473',
         u'\u8302\u540d': u'59659',
         u'\u8087\u5e86': u'59278',
         u'\u6c55\u5c3e ': u'59501',
         u'\u6cb3\u6e90': u'59293',
         u'\u63ed\u9633': u'59315',
         u'\u6885\u5dde': u'59117',
         u'\u4e2d\u5c71': u'59485',
         u'\u5fb7\u5e86': u'59269',
         u'\u9633\u6c5f': u'59663',
         u'\u4e91\u6d6e': u'59471',
         u'\u73e0\u6d77': u'59488',
         u'\u6c55\u5934': u'59316',
         u'\u4f5b\u5c71': u'59279',
         u'\u5357\u5b81': u'59432',
         u'\u6842\u6797': u'57957',
         u'\u9633\u6714': u'59051',
         u'\u67f3\u5dde': u'59046',
         u'\u68a7\u5dde': u'59265',
         u'\u7389\u6797': u'59453',
         u'\u6842\u5e73': u'59254',
         u'\u8d3a\u5dde': u'59065',
         u'\u94a6\u5dde': u'59632',
         u'\u8d35\u6e2f': u'59249',
         u'\u9632\u57ce\u6e2f': u'59635',
         u'\u767e\u8272': u'59211',
         u'\u5317\u6d77': u'59644',
         u'\u6cb3\u6c60': u'59023',
         u'\u6765\u5bbe': u'59242',
         u'\u5d07\u5de6': u'59425',
         u'\u6606\u660e': u'56778',
         u'\u4fdd\u5c71': u'56748',
         u'\u695a\u96c4': u'56768',
         u'\u5fb7\u5b8f': u'56844',
         u'\u7ea2\u6cb3': u'56975',
         u'\u4e34\u6ca7': u'56951',
         u'\u6012\u6c5f': u'56533',
         u'\u66f2\u9756': u'56783',
         u'\u601d\u8305': u'56964',
         u'\u6587\u5c71': u'56994',
         u'\u7389\u6eaa': u'56875',
         u'\u662d\u901a': u'56586',
         u'\u4e3d\u6c5f': u'56651',
         u'\u5927\u7406': u'56751',
         u'\u6d77\u53e3': u'59758',
         u'\u4e09\u4e9a': u'59948',
         u'\u510b\u5dde': u'59845',
         u'\u743c\u5c71': u'59757',
         u'\u901a\u4ec0': u'59941',
         u'\u6587\u660c': u'59856',
         u'\u4e4c\u9c81\u6728\u9f50': u'51463',
         u'\u963f\u52d2\u6cf0': u'51076',
         u'\u963f\u514b\u82cf': u'51628',
         u'\u660c\u5409': u'51368',
         u'\u54c8\u5bc6': u'52203',
         u'\u548c\u7530': u'51828',
         u'\u5580\u4ec0': u'51709',
         u'\u514b\u62c9\u739b\u4f9d': u'51243',
         u'\u77f3\u6cb3\u5b50': u'51356',
         u'\u5854\u57ce': u'51133',
         u'\u5e93\u5c14\u52d2': u'51656',
         u'\u5410\u9c81\u756a': u'51573',
         u'\u4f0a\u5b81': u'51431',
         u'\u62c9\u8428': u'55591',
         u'\u963f\u91cc': u'55437',
         u'\u660c\u90fd': u'56137',
         u'\u90a3\u66f2': u'55299',
         u'\u65e5\u5580\u5219': u'55578',
         u'\u5c71\u5357': u'55598',
         u'\u6797\u829d': u'56312',
         u'\u53f0\u5317': u'58968',
         u'\u9ad8\u96c4': u'59554'}


class WeatherStation(SGMLParser):

    def __init__(self, url):
        SGMLParser.__init__(self)
        self._is_weather, self._is_td = False, False
        self._page_datas, self._weather = None, []
        self._get_page_datas(url)
        self.feed(self._page_datas)
        return

    def _get_page_datas(self, url):
        sock = urllib.urlopen(url)
        lines = sock.read().split('\n')
        sock.close()
        lines1 = []
        for line in lines:
            try:
                l = line.decode('GB18030')
                lines1.append(l)
            except:
                pass

        self._page_datas = (u'\n').join(lines1)

    def start_td(self, attrs):
        self._is_td = True

    def end_td(self):
        self._is_td = False

    def handle_data(self, text):
        text = self._process_data(text)
        if text and self._is_weather:
            self._weather.append(text)
        if ('\xe6\x97\xb6\xe9\x97\xb4').decode('utf-8') in text:
            self._is_weather = True
        if ('\xe6\x8c\x87\xe6\x95\xb0\xe6\x9f\xa5\xe8\xaf\xa2').decode('utf-8') in text:
            self._is_weather = False

    def show(self):
        if len(self._weather) > 16:
            return self._weather[:12] + self._formatWinds(self._weather[12:])
        return self._weather

    def _formatWinds(self, li):
        s = ('\n').join(li)
        s = s.replace('\n<\n', '<')
        return s.split('\n')

    def _process_data(self, text):
        text = self._cut_words(text, ['\n', '\r', '\t', ' '])
        return text

    def _cut_words(self, text, words):
        if type(words) == type([]):
            for row in words:
                while row in text:
                    pos = text.index(row)
                    text = text[:pos] + text[pos + 1:]

        else:
            if words is not None:
                while words in text:
                    pos = text.index(words)
                    text = text[:pos] + text[pos + 1:]

        return text


WeatherDB = settings.ADDITION_FILE_ROOT + 'weather/'


def getWeather(area):
    if area is None:
        return
    try:
        areaID = citys[area]
    except Exception, e:
        try:
            areaID = citys[area.decode('GBK')]
        except Exception, e:
            areaID = area

    else:
        WeatherDir = WeatherDB + areaID
        today = str(datetime.datetime.now())[:10].replace('-', '')
        WeatherFile = WeatherDir + '/' + today + '.txt'
        if not os.path.isfile(WeatherFile):
            url = 'http://www.nmc.gov.cn/weatherdetail/%s.html' % (areaID,)
            try:
                lister = WeatherStation(url)
                datas = lister.show()[:16]
            except Exception, e:
                errorLog()
                datas = None
            else:
                try:
                    if datas and len(datas) == 16:
                        s = '%s\t%s\t%s\t%s\n%s\t%s\t%s\t%s\n%s\t%s\t%s\t%s\n' % (
                            datas[0], datas[4], datas[8], datas[12],
                            datas[1], datas[5], datas[9], datas[13],
                            datas[2], datas[6], datas[10], datas[14])
                        if not os.path.isdir(WeatherDir):
                            os.makedirs(WeatherDir)
                        open(WeatherFile, 'w+').write(s.encode('utf-8'))
                        return s.split('\n')
                except Exception, e:
                    errorLog()

        try:
            datas = open(WeatherFile, 'r').read().decode('utf-8').split('\n')
        except:
            datas = [
                u'NULL\n']

    return datas


def getWeatherCmd(device, wData):
    tft = device.IsTft()
    delta = datetime.datetime.now() - datetime.timedelta(0, 10800)
    if devcmds.objects.filter(CmdContent__startswith=tft and 'WEATHER MSG=' or 'SMS TYPE=IDLELCD', SN=device,
                              CmdCommitTime__gt=delta).count() > 0:
        return None
    if tft:
        return getWeatherCmdTFT(wData)
    return getWeatherCmdMono(wData)


WEATHER_PIC_INDEX = {u'\u6674': 'w1.gif',
                     u'\u6674\u95f4\u591a\u4e91': 'w2.gif',
                     u'\u6674\u8f6c\u591a\u4e91': 'w3.gif',
                     u'\u591a\u4e91\u8f6c\u9634': 'w4.gif',
                     u'\u5c0f\u96e8': 'w5.gif',
                     u'\u4e2d\u96e8': 'w6.gif',
                     u'\u5927\u96e8': 'w7.gif',
                     u'\u9635\u96e8': 'w11.gif'}


def getWeatherCmdTFT(wData):
    wd = []
    for d in wData:
        ds = d.split('\t')
        if len(ds) > 2:
            try:
                dpic = WEATHER_PIC_INDEX[ds[1]]
            except:
                dpic = 'w1.gif'
            else:
                ds.append(dpic)
                wd.append(('\t').join(ds))

    return u'WEATHER MSG=' + (u'\\n').join(wd)


def getWeatherCmdMono(wData):
    today_weather = formatWeather4iClock(wData[0])
    tomorrow_weather = formatWeather4iClock(wData[1])
    if today_weather is None or tomorrow_weather is None:
        return
    ss = today_weather + '                ' + tomorrow_weather
    return u'SMS TYPE=IDLELCD\tMSG=%s' % ss


def checkWeatherForDev(device):
    areaID = device.City
    if not areaID:
        return None
    datas = getWeather(areaID)
    if datas and u'NULL\n' not in datas:
        cmd = getWeatherCmd(device, datas)
        if cmd:
            return appendDevCmd(device, cmd)
    return datas


def formatWeather4iClock(u8):
    u = u8
    if u[-1] == '\n':
        u = u[:-1]
    arr = u.split('\t')
    ret = ''
    for row in arr:
        ret += gb_16(row)

    return ret


def gb_16(s):
    size = len(s.encode('gb2312'))
    count = (size + 15) / 16 * 16 - size
    return s + ' ' * count


def index(request):
    from django.http import HttpResponse
    device = iclock.objects.all().filter(SN='888888')[0]
    if get_Weather(device.Address.split('=')[1], device) is None:
        return HttpResponse('False')
    return HttpResponse('True')
