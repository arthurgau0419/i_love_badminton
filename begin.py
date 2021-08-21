from scrapy import cmdline
import os

# you can run this script using IDE.
# cmdline.execute("scrapy crawl badminton".split())
cmdline.execute(
    "scrapy crawl badminton -a account={} -a password={} -a fire_date={} -a date={} -a order_time={}  -a tp={} -a pt={} -a pid={}"
        .format(
            os.environ.get('account'),
            os.environ.get('password'),
            os.environ.get('fire_date'),
            os.environ.get('date'),
            os.environ.get('order_time'),
            os.environ.get('tp'),
            os.environ.get('pt'),
            os.environ.get('pid'),
    )
        .split()
)
