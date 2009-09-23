import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from gfinance.items import GfinanceItem


tickers_seen = set()

class GfinanceSpider(BaseSpider):
  domain_name = 'google.com'
  start_urls = ['http://www.google.com/finance',                
               ]
  
  def parse(self, response):
    hxs = HtmlXPathSelector(response)
    anchors = hxs.select('//a')
    items = []
    # TODO(fedele): refactor this into a CrawlSpider using rules.
    # TODO(fedele): write this so that it just grabs all financial/etc data
    ticker_regexp = re.compile(r'/finance\?q=([A-Za-z0-9:]+)')
    for anchor in anchors:      
      href = anchor.select('@href').extract()
      if not href:
        continue            
      m = ticker_regexp.search(href[0])
      if not m:
        continue
      ticker_symbol = m.groups(1)
      global tickers_seen
      if ticker_symbol in tickers_seen:
        continue
      print "found", ticker_symbol
      tickers_seen.add(ticker_symbol)
      item = GfinanceItem()      
      item['ticker'] = ticker_symbol
      items.append(item)
    return items   

    
SPIDER = GfinanceSpider()