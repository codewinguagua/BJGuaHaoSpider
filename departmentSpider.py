# -*- coding: UTF-8 -*-

import re
import urllib.request
import urllib.error
import urllib.parse
import timeSpider
import Validator

# 获取科室信息类
class DepartmentInfo:

    # 初始化方法
    def __init__(self, baseUrl):
        # base链接
        self.baseUrl = baseUrl
        # 科室列表信息
        self.departments = []

    # 返回科室列表
    def getDepartments(self, pageCode):
        # 生成获取科室信息的正则表达式对象
        pattern = re.compile('<a class="kfyuks_islogin" href="(.*?)">(.*?)</a>', re.S)
        items = re.findall(pattern, pageCode)

        # 遍历结果
        for item in items:
            print(item[0], item[1])

            if Validator.compileurl(self.baseUrl + item[0]):
                ids = self.parseUrl(item[0])
                self.departments.append([item[0], item[1], ids[0], ids[1]])
            else:
                result = self.combineUrlComponent(item[0])
                self.departments.append([result[0], item[1], result[1], result[2]])

        return self.departments

    # 加载网页
    def loadPage(self, subPath):
        url = self.baseUrl + subPath
        # request对象
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)

        return response.read().decode('utf-8')

    # 组装url
    def combineUrlComponent(self, item):
        subItem = item[len('javascript:encodeUrl('):len(item)-2].split(',')
        subPath = '/dpt/appoints/%s,%s.htm?departmentName=%s&deptSpec=%s' % (subItem[0].strip('\''),
                                                                             subItem[1].strip('\''),
                                                                             urllib.parse.quote(subItem[2].strip('\'').encode('utf-8')),
                                                                             urllib.parse.quote(subItem[3].strip('\'').encode('utf-8')))

        return [subPath, subItem[0].strip('\''), subItem[1].strip('\'')]

    def parseUrl(self, subPath):
        # 正则表达式对象 url e.g.:/dpt/appoint/3-200000002.htm
        print(subPath)
        pattern = re.compile('.*/(.*?)-(.*?).htm', re.S)
        result = re.search(pattern, subPath)

        if not result:
            print('解析url获取医院id和科室id失败')
            return None

        self.hospitalId = result.group(1).strip()
        self.departmentId = result.group(2).strip()
        print('医院ID:%s\t科室ID：%s' % (self.hospitalId, self.departmentId))

        return [self.hospitalId, self.departmentId]

    # 开始方法
    def start(self, subPath):
        pageCode = self.loadPage(subPath)
        # 抓取科室信息
        self.getDepartments(pageCode)

        # 轮询科室列表并抓取科室预约号信息
        ts = timeSpider.timeSpider(self.baseUrl)
        for department in self.departments:
            # print(department)
            ts.start(department[0], department[2], department[3])

if __name__ == '__main__':
    baseUrl = 'http://www.bjguahao.gov.cn'
    di = DepartmentInfo(baseUrl)
    di.start('/hp/appoint/91.htm')
