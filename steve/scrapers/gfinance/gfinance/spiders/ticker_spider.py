import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from gfinance.items import GfinanceItem

class GfinanceSpider(BaseSpider):
  domain_name = 'dmoz.org'
  start_urls = ['http://www.google.com/finance',                
               ]
               
  def __init__(self, *args, **kwargs):
    super(GfinanceSpider, self).__init__(self, *args, **kwargs)
    self.tickers_seen = set()
  
  def parse(self, response):
    hxs = HtmlXPathSelector(response)
    anchors = hxs.select('//a')
    items = []
    ticker_regexp = re.compile(r'/finance\?q=([A-Za-z0-9:]+')
    for anchor in anchors:      
      href = anchor.select('/@href').extract()
      m = ticker_regexp.search(href)
      if not m:
        continue
      ticker_symbol = m.groups(1)
      if ticker_symbol in self.tickers_seen:
        continue
      print "found", ticker_symbol
      self.tickers_seen.add(ticker_symbol)
      item = GfinanceItem()      
      item['ticker'] = ticker_symbol
      items.append(item)
    return items   
    
SPIDER = GfinanceSpider()