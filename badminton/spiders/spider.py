import scrapy
import re
from img import convert_image, change_image_to_text, get_image
import time
import datetime

class BadmintonSpider(scrapy.Spider):

    name = 'badminton'

    account = None
    password = None
    date = None
    order_time = None
    tp = None
    pt = None
    pid = None
    fire_datetime = None
    srv_datetime = None

    tz = datetime.timezone(datetime.timedelta(hours=+8))

    def __init__(self, account, password, fire_date, date, order_time, tp, pt, pid, **kwargs):
        self.account = account
        self.password = password
        self.date = date
        self.order_time = order_time
        self.tp = tp
        self.pt = pt
        self.pid = pid

        self.fire_datetime = datetime.datetime.strptime(fire_date, '%Y/%m/%d')\
            .replace(tzinfo=self.tz)\
            .astimezone(datetime.timezone.utc)

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
        self.update_srv_datetime(response)
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
            time_list = self.order_time.split(',')
            pid_list = self.pid.split(',')
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
                cb_kwargs={
                    'time_list': time_list,
                    'pid_list': pid_list
                }
            )
        else:
            yield self.captcha_request(login_response, captcha_url)

    def order_request(self, response, order_time, pid):

        path = 'tp{}.aspx?module=net_booking&files=booking_place&StepFlag=25&QPid={}&QTime={}&PT={}&D={}'.format(
            self.tp,
            pid,
            order_time,
            self.pt,
            self.date
        )

        return scrapy.Request(
            response.urljoin(path),
            callback=self.parse,
            errback=self.do_order,
            dont_filter=True,
            cb_kwargs={
                'time_list': [order_time],
                'pid_list': [pid]
            }
        )

    def do_order(self, response, *args, **kwargs):
        now = datetime.datetime.now(tz=self.tz) \
            .astimezone(datetime.timezone.utc)
        seconds_to_fire = (self.fire_datetime - now).total_seconds()
        if seconds_to_fire < -10:
            print('已超過十秒，結束')
            return

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
            if seconds_to_fire > 3:
                print('還剩: {} 秒開始，等待中...'.format(seconds_to_fire))
                time.sleep(seconds_to_fire - 3)
            time_list = kwargs.get('time_list', [])
            pid_list = kwargs.get('pid_list', [])
            for pid in pid_list:
                for order_time in time_list:
                    yield self.order_request(response, order_time=order_time, pid=pid)

    def parse(self, response, *args, **kwargs):
        content = response.body.decode('utf8')
        pattern = "tp{}\.aspx\?module=net_booking&files=booking_place&X=(\d+)&Y=(\d+)&StepFlag=3".format(self.tp)
        matchs = re.findall(pattern, content)
        match = next(iter(matchs), None)
        if match:
            result = match[0]
            if result != '1':
                time_list = kwargs.get('time_list', [])
                pid_list = kwargs.get('pid_list', [])
                for order_time in time_list:
                    for pid in pid_list:
                        yield self.order_request(response, order_time=order_time, pid=pid)
            else:
                order = match[1]
                # todo: parse time, pid
                text = "預定成功(日期:{} 時段:{} 場地:{})，訂單號碼為: {}".format(self.date, self.order_time, self.pid, order)
                yield {'success': text}
        else:
            # 代表需要重新登入
            yield scrapy.Request(
                'https://scr.cyc.org.tw/tp{}.aspx?module=login_page&files=login'.format(self.tp),
                callback=self.parse_login,
                dont_filter=True
            )

    def update_srv_datetime(self, response):
        date = response.headers.get('Date')
        if date:
            self.srv_datetime = datetime.datetime \
                .strptime(date.decode("utf-8"), '%a, %d %b %Y %H:%M:%S %Z') \
                .replace(tzinfo=datetime.timezone.utc)
