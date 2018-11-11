# encoding:utf-8
"""
@Author : Rilzob
@Time : 18-9-26上午10:55
"""

import scrapy
from selenium import webdriver


from scrapy.loader import ItemLoader

class ZhihuSpider(scrapy.Spider):
    name = "zhihu_sel"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    def start_requests(self):
        browser = webdriver.Chrome(executable_path="/home/Rilzob/公共/Articlespider/chromedriver")
        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[2]/div[1]/form/div[1]/div[2]/div[1]/input").send_keys("15724428236")
        browser.find_element_by_xpath("//*[@id='root']/div/main/div/div/div/div[2]/div[1]/form/div[2]/div/div[1]/input").send_keys("watermirrorsir")
        browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/button').click()
        import time
        time.sleep(10)
        Cookies = browser.get_cookies()
        print(Cookies)
        cookie_dict = {}
        import pickle
        for cookie in Cookies:
            # 写入文件
            f = open('/home/Rilzob/公共/Articlespider/cookies/zhihu' + cookie['name'] + '.zhihu', 'wb')
            pickle.dump(cookie, f)
            f.close()
            cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

    def login(self, response):
        pass
