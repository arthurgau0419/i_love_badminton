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
    tp = None
    pt = None
    pid = None

    def __init__(self, account, password, date, order_time, tp, pt, pid, **kwargs):
        self.account = account
        self.password = password
        self.date = date
        self.order_time = order_time
        self.tp = tp
        self.pt = pt
        self.pid = pid
        super().__init__(**kwargs)

    def start_requests(self):
        yield scrapy.Request(
            'https://scr.cyc.org.tw/tp{}.aspx?module=login_page&files=login'.format(self.tp),
            callback=self.parse_login,
            dont_filter=True
        )

    def captcha_request(self, login_response, captcha_url):
        return scrapy.Request(
            captcha_url,
            meta={
                'login_response': login_response,
                'captcha_url': captcha_url
            },
            callback=self.login,
            dont_filter=True,
        )

    def parse_login(self, response):
        captcha_src = response.xpath('//img[@id="ContentPlaceHolder1_CaptchaImage"]/@src').extract_first()
        captcha_url = response.urljoin(captcha_src)
        yield self.captcha_request(response, captcha_url)

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
            self.log("驗證碼為: {}".format(text))
            yield scrapy.FormRequest(
                login_response.urljoin('tp{}.aspx?module=login_page&files=login'.format(self.tp)),
                method='POST',
                formdata={
                    'loginid': self.account,
                    'loginpw': self.password,
                    'Captcha_text': text
                },
                callback=self.do_order,
                dont_filter=True,
                meta={
                    'login_response': login_response,
                    'captcha_url': captcha_url
                },
            )
        else:
            yield self.captcha_request(login_response, captcha_url)

    def order_request(self, response):

        path = 'tp{}.aspx?module=net_booking&files=booking_place&StepFlag=25&QPid={}&QTime={}&PT={}&D={}'.format(
            self.tp,
            self.pid,
            self.order_time,
            self.pt,
            self.date
        )

        return scrapy.Request(
            response.urljoin(path),
            callback=self.parse,
            errback=self.do_order,
            dont_filter=True,
        )

    def do_order(self, response):
        login_response = response.meta.get('login_response')
        captcha_url = response.meta.get('captcha_url')
        # 去看他們前端真的就這樣趴
        args = response.text.split(',')
        result = next(iter(args), None)
        if result == '1':
            self.log('帳號密碼錯誤')
        elif result == '2':
            self.log(args[1])
            if args[1] == '驗證碼錯誤':
                yield self.captcha_request(login_response, captcha_url)
        elif result == '3':
            yield self.captcha_request(login_response, captcha_url)
        else:
            yield self.order_request(response)

    def parse(self, response):
        content = response.body.decode('utf8')
        pattern = "tp{}\.aspx\?module=net_booking&files=booking_place&X=(\d+)&Y=(\d+)&StepFlag=3".format(self.tp)
        matchs = re.findall(pattern, content)
        match = next(iter(matchs), None)
        if match:
            result = match[0]
            if result != '1':
                delay = 1
                self.log("預定失敗，({})秒後再試...".format(delay))
                # 客氣一點
                # time.sleep(delay)
                yield self.order_request(response)
            else:
                order = match[1]
                self.log("預定成功(日期:{} 時段:{} 場地:{})，訂單號碼為: {}".format(self.date, self.order_time, self.pid, order))
        else:
            # 代表需要重新登入
            yield scrapy.Request(
                'https://scr.cyc.org.tw/tp{}.aspx?module=login_page&files=login'.format(self.tp),
                callback=self.parse_login,
                dont_filter=True
            )