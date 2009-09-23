# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

class GfinancePipeline(object):
  def __init__(self):
    self.f = open('ticker_symbols.txt', 'w')
  
  def process_item(self, domain, item):
    print >> self.f, item['ticker'][0]
    return item
