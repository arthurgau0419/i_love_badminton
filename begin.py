from scrapy import cmdline

# you can run this script using IDE.
# cmdline.execute("scrapy crawl badminton".split())
cmdline.execute("scrapy crawl badminton -a account=ooo -a password=xxx -a date=2019/10/02 -a order_time=20 -a pid=87".split())
