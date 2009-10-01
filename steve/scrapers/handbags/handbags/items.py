# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib_exp.djangoitem import DjangoItem

from cobra.steve.webapps.handbags.bags.models import Handbag


class HandbagItem(DjangoItem):
  django_model = Handbag
