# -*- coding: UTF-8 -*-

import re
import urllib.request
import urllib.error
import timeSpider

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
            print(item[0],item[1])
            self.departments.append([item[0], item[1]])

        return self.departments

    # 加载网页
    def loadPage(self, subPath):
        url = self.baseUrl + subPath
        print(url)
        # request对象
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)

        return response.read().decode('utf-8')

    # 开始方法
    def start(self, subPath):
        pageCode = self.loadPage(subPath)
        # 抓取科室信息
        self.getDepartments(pageCode)

        # 轮询科室列表并抓取科室预约号信息
        ts = timeSpider.timeSpider(self.baseUrl)
        for department in self.departments:
            department.append(ts.start(department[0]))

if __name__ == '__main__':
    baseUrl = 'http://www.bjguahao.gov.cn'
    di = DepartmentInfo(baseUrl)
    di.start('/hp/appoint/3.htm')
