# -*- coding: UTF-8 -*-

import urllib.request
import urllib.error
import re
import departmentSpider

# 北京市预约挂号平台爬虫
class BJGuaHaoSpider:

    # 初始化函数
    def __init__(self, baseUrl):
        # base链接
        self.baseUrl = baseUrl
        # 保存医院信息列表
        self.hospitals = []
        # 医院页面总页数
        self.pageNum = 0

    # 抓取网页
    def getPage(self, subPath):
        url = self.baseUrl + subPath
        print(url)
        # 生成请求网页的request
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)

        # 返回网页数据
        return response.read().decode('utf-8')

    # 解析页面并返回医院列表,医院信息包括(医院名称,医院地址)
    def getHospitals(self, pageCode):
        # 生成获取医院信息的正则表达式对象
        pattern = re.compile('<div.*?yiyuan_content_1".*?class="yiyuan_co_titl".*?href="(.*?)">(.*?)</a>', re.S)
        items = re.findall(pattern, pageCode)

        # 遍历结果列表
        for item in items:
            # print item
            # 获取每个医院的名称和链接,item[1]为医院名称,item[0]为链接
            self.hospitals.append({"hpname": item[1].strip(), 'hplink': item[0].strip()})

    # 获取页数
    def getPageNum(self, pageCode):
        # 生成获取总页数的正则表达式
        pattern = re.compile(u'<div id="yiyuan_list_rq".*?共(.*?)页</li>', re.S)
        result = re.search(pattern, pageCode)

        return int(result.group(1).strip())

    # 抓取科室信息
    def getDepartments(self, subPath):
        ds = departmentSpider.DepartmentInfo(self.baseUrl)
        departments = ds.start(subPath)
        return departments

    # 开始方法
    def start(self):
        pageCode = self.getPage('/hp.htm')
        self.pageNum = self.getPageNum(pageCode)
        print(self.pageNum)

        # 从第一页到最后一页进行遍历
        for i in range(1, self.pageNum+1):
            subPath = '/hp/%d,0,0,0.htm' % (i)
            pageCode = self.getPage(subPath)

            if pageCode is not None:
                self.getHospitals(pageCode)
            else:
                print('获取网页失败')

        # 获取医院下的科室列表
        for hospital in self.hospitals:
            print('医院:%s\t链接:%s\n' % (hospital['hpname'], hospital['hplink']))
            hospital['hpdepartment'] = self.getDepartments(hospital['hplink'])

if __name__ == '__main__':
    baseUrl = 'http://www.bjguahao.gov.cn'
    spider = BJGuaHaoSpider(baseUrl)
    spider.start()
