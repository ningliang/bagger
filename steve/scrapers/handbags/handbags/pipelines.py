# Define your item pipelines here


class HandbagPipeline(object):
  def process_item(self, domain, item):
    item.save()
    return item
