# -*- coding: utf-8 -*-
import scrapy
import re
import json
try:
    from urllib import parse
except:
    import urlparse as parse
from scrapy.loader import ItemLoader
import datetime

from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # question的第一页answer的请求url
    start_answer_url = ""

    def parse(self, response):
        '''
        提取出html页面中的所有url并跟踪这些url进行下一步爬取
        如果提取的url中格式为/question/xxx就下载之后直接进入解析函数
        :param response:
        :return:
        '''
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startwith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$)", response.url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面，从页面中提取出具体的question item
        if "QuestionHeader-title" in response.text:
            # 处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$)", response.url)
            if match_obj:
                question_id = match_obj.group(2)
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-actions button::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

            question_item = item_loader.load_item()
        else:
            # 处理老版本页面的item提取
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$)", response.url)
            if match_obj:
                question_id = match_obj.group(2)
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title", "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num", "//*[@id='zh-question-side-header-wrap']/text()|//*[@class]='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer['author'] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = match_obj.group(1)

        if xsrf:
            post_url = 'https://www.zhihu.com/login/phone_num'
            post_data = {
                "_xsrf": xsrf,
                "phone_num": 15724428236,
                "password": "watermirrorsir",
                "captcha": ""
            }

            import time
            t = str(int(time.time() * 1000))
            captcha_url = 'https://www.zhihu.com/captcha.git?r={0}&type=login'.format(t)
            captcha_url_cn = 'https://www.zhihu.com/captcha.git?r={0}&type=login&lang=cn'.format(t)
            yield scrapy.Request(captcha_url_cn, headers=self.headers, meta={"post_data":post_data}, callback=self.login_after_captcha_cn)
            yield scrapy.Request(captcha_url, headers=self.headers, meta={"post_data":post_data}, callback=self.login_after_captcha)

    def login_after_captcha_cn(self, response):
        # 知乎倒立汉字验证码识别登录
        with open("captcha.jpg", "wb") as f:
            f.write(response.boby)
            f.close()

        from zheye import zheye
        z = zheye()
        positions = z.Recognize('captcha.jpg')

        pos_arr = []
        if len(positions) == 2:
            if positions[0][1] > positions[1][1]:
                pos_arr.append([positions[1][1], positions[1][0]])
                pos_arr.append([positions[0][1], positions[0][0]])
            else:
                pos_arr.append([positions[0][1], positions[0][0]])
                pos_arr.append([positions[1][1], positions[1][0]])
        else:
            pos_arr.append([positions[0][1], positions[0][0]])

        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = response.meta.get("post_data", {})
        if len(positions) == 2:
            post_data["captcha"] = '{"img_size": [200, 44], "input_points": [[%.2f, %f], [%.2f, %f]]}' % (
                pos_arr[0][1] / 2, pos_arr[0][0] / 2, pos_arr[1][1] / 2, pos_arr[1][0] / 2)
        else:
            post_data["captcha"] = '{"img_size": [200, 44], "input_points": [[%.2f, %f]}' % (
                pos_arr[0][1] / 2, pos_arr[0][0] / 2)
        post_data['captcha_type'] = 'cn'
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def login_after_captcha(self, response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.boby)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        captcha = input("输入验证码\n>")

        post_data = response.meta.get("post_data", {})
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def check_login(self, response):
        # 验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)