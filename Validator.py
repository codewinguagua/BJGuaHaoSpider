#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: 朱有凑
@license: Apache Licence
@contact: zhuyoucou@tianshiguahao.com
@site: http://www.weibo.com
@software: PyCharm
@file: Validator.py
@time: 2016/3/15 10:09
"""

import re

def compileurl(url):
    pattern = re.compile(r'^(?:http|ftp)s?://' # http:// or https://
                         r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                         r'localhost|' #localhost...
                         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                         r'(?::\d+)?' # optional port
                         r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    result = re.match(pattern, url)

    if result:
        return True
    else:
        return False