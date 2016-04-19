# -*- coding: UTF-8 -*-

import re
import urllib.request
import urllib.error
from urllib import parse
import json
import datetime
import time
import Validator

# 获取时间信息
class timeSpider:

    # 初始化方法
    def __init__(self, baseUrl):
        # base链接
        self.baseUrl = baseUrl
        # 医院ID
        self.hospitalId = None
        # 科室ID
        self.departmentId = None
        # 存放可预约天数,默认一周(7天)
        self.days = 7
        # 存放日期列表
        self.dates = []
        # 获取挂号详情信息的url
        self.postUrl = 'http://www.bjguahao.gov.cn/dpt/partduty.htm'

    # 获取页面编码
    def loadPage(self, subPath):
        url = self.baseUrl + subPath
        print(url)

        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)

        return response.read().decode('utf-8')

    # 获取日期信息
    def getTimes(self, pageCode):
        # 生成获取日期信息的正则表达式对象
        pattern = re.compile('<div class="ksorder_cen_l_t_c".*?>', re.S)
        items = re.findall(pattern, pageCode)

        # 遍历正则匹配结果
        for item in items:
            print(item)

        return self.times

    # 抓取指定日期下的可预约号信息
    def getInformationInDate(self, pageCode, day, colnum):
        # 正则表达式对象
        value1 = '1_%s' % day      # 上午
        value2 = '2_%s' % day      # 下午
        value3 = '4_%s' % day      # 晚上
        items = None
        # 将第一列与后面的列分开处理
        if colnum == 0:
            # 取第一列信息的正则表达式
            patternstr = '<div class="ksorder_cen_l_t_c"' \
                         '(.*?)value=".*?%s".*?</tr>' \
                         '(.*?)value=".*?%s".*?</tr>' \
                         '(.*?)value=".*?%s".*?</tr>' % (value1, value2, value3)
            pattern = re.compile(patternstr, re.S)
            items = re.findall(pattern, pageCode)
        else:
            # 取第一列以后列信息的正则表达式
            name = 'col_%d' % (colnum-1)
            patternstr = '<div class="ksorder_cen_l_t_c"' \
                         '.*?name="%s".*?>(.*?)value=".*?%s".*?</tr>' \
                         '.*?name="%s".*?>(.*?)value=".*?%s".*?</tr>' \
                         '.*?name="%s".*?>(.*?)value=".*?%s".*?</tr>' % (name, value1, name, value2, name, value3)

            # print patternstr
            pattern = re.compile(patternstr, re.S)
            items = re.findall(pattern, pageCode)

        return self.parseResult(items, day)

    # 模拟post方法
    def post(self, url, args):
        # 构建参数
        data = parse.urlencode(args)
        data = data.encode('ascii')
        # request对象
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            the_page = response.read().decode('utf-8')

        data = json.loads(the_page)
        # print(data['data'][0]['doctorTitleName'])
        return data['data'][0]

    # 分析可预约号匹配结果并返回
    def parseResult(self, items, day):
        # 分析匹配结果
        dayInfo = {}
        for item in items:
            for i in range(0, 3):
                haveKYY = re.search('ksorder_kyy', item[i])
                leastnum = 0
                keyname = '%d_%s' % (4 if i == 2 else i, day)
                if haveKYY:
                    # 抓取剩余可预约数量
                    pattern = re.compile(u'剩余:(.*?)<input', re.S)
                    leastnum = int(re.search(pattern, item[i]).group(1).strip())
                    # 抓取挂号费等详细信息
                    self.getDetail(4 if i == 2 else i, day)

                dayInfo[keyname] = leastnum

        return dayInfo

    # 如果存在可预约号则调用该方法获取挂号费等信息
    def getDetail(self, dutycode, dutydate):
        args = {}
        args['hospitalId'] = self.hospitalId
        args['departmentId'] = self.departmentId
        args['dutyCode'] = 2 if dutycode == 1 else 1
        args['dutyDate'] = dutydate
        args['isAjax'] = 'true'

        data = self.post(self.postUrl, args)

        print('医生：%s\t擅长：%s\t挂号费：￥%s\t剩余：%s' % (data['doctorTitleName'], data['skill'], data['totalFee'], data['remainAvailableNumber']))
        return [data['doctorTitleName'], data['skill'], data['totalFee'], data['remainAvailableNumber']]

    # 取出可预约的日期列表
    def getKYYDate(self, pageCode):
        # 生成获取可预约日期列表的正则表达式
        pattern = re.compile('scope="col">(.*?)<p>(.*?)</p></th>', re.S)
        items = re.findall(pattern, pageCode)

        # 遍历匹配结果
        colnum = 0
        for item in items:
            print('%s\t%s' % (item[0], item[1]))
            self.dates.append([item[0].strip(), item[1].strip()])
            # 抓取当前日期下的可预约情况
            self.dates.append(self.getInformationInDate(pageCode, item[1].strip(), colnum))
            # 列加1
            colnum += 1

        print
        return self.dates

    # 取出所有可预约日期列表及对应的每天剩余可预约数
    def getAllKYYDate(self, pageCode):
        self.days = int(self.getKYYDays(pageCode))
        # 根据天数计算可预约周数
        weeknum = self.days/7
        # 获取当前页日期信息
        self.getKYYDate(pageCode)

        while weeknum>1:
            # 获取下一页link
            pattern = re.compile('<div class="ksorder_cen_l_r">.*?href="(.*?)".*?></a>', re.S)
            result = re.search(pattern, pageCode)

            link = result.group(1).strip()
            print(link)

            if not Validator.compileurl(self.baseUrl + link):
                link = self.combineUrlComponent(link)
            pageCode = self.loadPage(link)
            self.getKYYDate(pageCode)
            # 可预约周数减1
            weeknum -= 1

    # 组装url
    def combineUrlComponent(self, item):
        subItem = item[len('javascript:urlEncodeing('):len(item)-1].split(',')
        subPath = '/dpt/appoints/%s,%s.htm?week=%s&departmentName=%s' % (subItem[0].strip('\''),
                                                                             subItem[1].strip('\''),
                                                                             urllib.parse.quote(subItem[2].strip('\'').encode('utf-8')),
                                                                             urllib.parse.quote(subItem[3].strip('\'').encode('utf-8')))

        return subPath

    # 获取预约周期
    def getKYYDays(self, pageCode):
        # 生成获取天数的正则表达式对象
        pattern = re.compile(u'<div class="ksorder_cen_r_top">.*?预约周期.*?</span>(.*?)<script.*?</li>', re.S)
        result = re.search(pattern, pageCode)

        if not result:
            print('获取预约周期失败')

        return result.group(1).strip()

    # 开始方法
    def start(self, subPath, hospital_id, department_id):
        self.subPath = subPath
        self.hospitalId = hospital_id
        self.departmentId = department_id
        # 抓取网页
        pageCode = self.loadPage(subPath)
        # 抓取每天的日期信息
        if not pageCode:
            print('抓取网页失败')
            return None

        self.getInformationInDate(pageCode, '2016-03-19', 0)
        # self.getKYYDate(pageCode)
        # self.getAllKYYDate(pageCode)

        return self.dates

gl_begin_time = datetime.datetime.now()
gl_end_time = gl_begin_time + datetime.timedelta(minutes=60)
if __name__ == '__main__':
    while datetime.datetime.now() < gl_end_time:
        baseUrl = 'http://www.bjguahao.gov.cn'
        ts = timeSpider(baseUrl)
        ts.start('/dpt/appoint/225-200003594.htm', '225', '200003594')
        print(datetime.datetime.now())
        time.sleep(0.1)
    print('\n\n\nend\n\n\n')

