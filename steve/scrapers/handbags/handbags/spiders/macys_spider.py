from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.conf import settings

from handbags.items import HandbagItem

import os.path
import random
import re
from functools import partial


class MacysSpider(BaseSpider):
  domain_name = 'macys.com'
  start_urls = ['http://www1.macys.com/catalog/index.ognc?CategoryID=26846&PageID=115303442966278']
  
  def parse(self, response):
    # Extract links to the category pages.    
    hxs = HtmlXPathSelector(response)
    category_urls = hxs.select('//tr[contains(@id, "menu_id_5")]/td/a/@href').extract()
    return [Request(url=url, callback=self.parse_category_page) for url in category_urls]
    
  def parse_category_page(self, response):
    hxs = HtmlXPathSelector(response)
    # Extract next page links    
    next_page_urls = hxs.select("//a[@class='depthPathLinked']/@href").extract()
    items = [Request(url=url, callback=self.parse_category_page) for url in next_page_urls]    
    # Extract all items on the page.  Also extract the thumbnails.
    handbag_anchors = hxs.select("//td[@class='productThumb']/div/a")
    for anchor in handbag_anchors:
      url = anchor.select('@href').extract()[0]
      tmp = anchor.select('img/@src').extract()
      # Some anchors appear multiple times in the same grid entry, but only one will
      # have an image inside it.  Filter all the ones that don't.
      if not tmp:
        continue
      image_url = tmp[0]
      # Macy's specifies the image width in the url.  Rather than fetch the thumbnail,
      # we change the url to fetch a bigger image.  327 is the width they use on product
      # detail pages:
      image_url = re.sub(r'wid=\d+', 'wid=327', image_url)
      random_image_id = random.randint(0, 10**9 - 1)
      image_path = os.path.join(settings.get('IMAGES_DIRECTORY'), "orig-%09d.jpg" % random_image_id)
      items.append(Request(url=url, callback=partial(self.parse_detail_page, image_path)))
      items.append(Request(url=image_url, callback=partial(self.parse_image, image_path)))
    return items
    
  def parse_detail_page(self, image_path, response):
    hxs = HtmlXPathSelector(response)    
    bag = HandbagItem()
    bag['name'] = hxs.select("//h1[@class='productDetailShort']/text()").extract()[0]
    breadcrumbs = hxs.select("//div[@class='breadCrumbs']/h2/a/text()").extract()
    bag['bag_type'] = " ".join(breadcrumbs[1:-1])
    price = hxs.select("//span[@class='productDetailPrice']/text()").extract()[0]    
    bag['price'] = re.search(r'\$(\d+\.\d+)', price).group(1)
    bag['original_image_path'] = image_path
    # There's no obvious way to extract brand here... its usually the first part of the name.
    # bag['brand'] = None
    bag['link'] = response.url
    bag['colors'] = " %s " % " ".join(hxs.select("//div[@class='swatchClickable']/@title").extract()).lower()    
    short_description = hxs.select("//div[@class='productDetailLong']/text()").extract()[0]
    raw_descriptions = hxs.select("//div[@id='pdpInfoTab1_content']/ul[@class='prodInfoList']/li/text()").extract()    
    description_list = '\n'.join("* %s" % x for x in filter(None, map(unicode.strip, raw_descriptions)))
    bag['description'] = "%s\n\n%s" % (short_description, description_list)
    return [bag]
    
  def parse_image(self, image_path, response):
    f = open(image_path, 'wb')
    f.write(response.body)
    f.close()
    return []

    
SPIDER = MacysSpider()