import scrapy
import re
from img import convert_image, change_image_to_text, get_image
import time

class BadmintonSpider(scrapy.Spider):

    name = 'badminton'

    account = None
    password = None
    date = None
    order_time = None
    pid = None

    def __init__(self, account, password, date, order_time, pid, **kwargs):
        self.account = account
        self.password = password
        self.date = date
        self.order_time = order_time
        self.pid = pid
        super().__init__(**kwargs)

    def start_requests(self):
        yield scrapy.Request(
            'https://scr.cyc.org.tw/tp12.aspx?module=login_page&files=login',
            callback=self.parse_login
        )

    def parse_login(self, response):
        captcha_src = response.xpath('//img[@id="ContentPlaceHolder1_CaptchaImage"]/@src').extract_first()
        captcha_url = response.urljoin(captcha_src)
        yield scrapy.Request(
            captcha_url,
            meta={
                'login_response': response,
                'captcha_url': captcha_url
            },
            callback=self.login,
            dont_filter=True,
        )

    def login(self, response):
        login_response = response.meta.get('login_response')
        captcha_url = response.meta.get('captcha_url')
        captcha_data = response.body
        fo = open('captcha.gif', 'wb')
        fo.write(captcha_data)
        fo.close()
        img = get_image('captcha.gif')
        img = convert_image(img)
        text = change_image_to_text(img)
        it = iter(re.findall('([0-9]{5})', text))
        text = next(it, None)
        if text:
            print(text)
            yield scrapy.FormRequest(
                login_response.urljoin('tp12.aspx?module=login_page&files=login'),
                method='POST',
                formdata={
                    'loginid': self.account,
                    'loginpw': self.password,
                    'Captcha_text': text
                },
                callback=self.do_order
            )
        else:
            yield scrapy.Request(
                captcha_url,
                meta={
                    'login_response': login_response,
                    'captcha_url': captcha_url
                },
                callback=self.login,
                dont_filter=True,
            )

    def order_request(self, response):

        path = 'tp12.aspx?module=net_booking&files=booking_place&StepFlag=25&QPid={}&QTime={}&PT=1&D={}'.format(
            self.pid,
            self.order_time,
            self.date
        )

        return scrapy.Request(
            response.urljoin(path),
            callback=self.parse,
            errback=self.do_order,
            dont_filter=True,
        )

    def do_order(self, response):
        yield self.order_request(response)

    def parse(self, response):
        content = response.body.decode()
        print(re.match("<script> window.location.href=\\'../../../tp12.aspx\?module=net_booking&files=booking_place&X=1&Y=([0-9]{2,})&StepFlag=3\\' </script>", content))
        if re.match("<script> window.location.href=\\'../../../tp12.aspx\?module=net_booking&files=booking_place&X=1&Y=([0-9]{2,})&StepFlag=3\\' </script>", content):
            match = next(iter(re.findall("<script> window.location.href=\\'../../../tp12.aspx\?module=net_booking&files=booking_place&X=1&Y=([0-9]{2,})&StepFlag=3\\' </script>", content)), None)
            print(match)
        else:
            print('retry')
            # 客氣一點
            time.sleep(1)
            yield self.order_request(response)