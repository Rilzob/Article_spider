# encoding:utf-8
"""
@Author : Rilzob
@Time : 18-9-28下午4:46
"""
from zheye import zheye
z = zheye()
positions = z.Recognize('captcha_cn.gif')
print(positions)