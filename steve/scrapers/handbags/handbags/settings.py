# Scrapy settings for handbags project
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

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'cobra.steve.webapps.handbags.settings'
assert "DJANGO_SETTINGS_MODULE" in os.environ

import cobra.steve.webapps.handbags.settings as django_settings
ROOT_DATA_DIRECTORY = django_settings.ROOT_DATA_DIRECTORY
IMAGES_DIRECTORY    = django_settings.IMAGES_DIRECTORY

import handbags

BOT_NAME = 'handbags'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['handbags.spiders']
NEWSPIDER_MODULE = 'handbags.spiders'
DEFAULT_ITEM_CLASS = 'handbags.items.HandbagItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

HTTPCACHE_DIR = 'C:/data/handbags/crawlcache'
# HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24

ITEM_PIPELINES = [
  'handbags.pipelines.HandbagPipeline'
]
