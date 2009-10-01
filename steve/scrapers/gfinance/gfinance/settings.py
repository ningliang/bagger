# Scrapy settings for gfinance project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# Or you can copy and paste them from where they're defined in Scrapy:
# 
#     scrapy/conf/default_settings.py
#

import gfinance

BOT_NAME = 'gfinance'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['gfinance.spiders']
NEWSPIDER_MODULE = 'gfinance.spiders'
DEFAULT_ITEM_CLASS = 'gfinance.items.GfinanceItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
ITEM_PIPELINES = ['gfinance.pipelines.GfinancePipeline']

