import json

from cobra.steve.util.prelude import *
from cobra.steve.crawler import grawler, caches
from cobra.steve.indexing.proto import handbag_pb2
from cobra.steve.indexing import protokv


def FindAllClass(soup, tag, class_rx):
  """Helper method that finds all tags with a class attribute that matches class_rx."""
  return soup.findAll(tag, attrs={'class': re.compile(class_rx)})


def PrettyPrintDict(mydict, indent=0):
  indent_str = "  " * indent
  for key, value in sorted(mydict.items()):
    if isinstance(value, dict):
      print key
      PrettyPrintDict(value, indent+1)
    else:
      print indent_str, "[%-20s] %s" % (key, value)


def CoachProcessCategoryPage(url, soup, EmitUrl, Output):
  # Find all category links on this page.
  for li in FindAllClass(soup, 'li', 'navFeatures'):
    a = li.a
    if a is None:
      continue
    category = a.contents[0].strip()
    link_url = a['href']
    if 'handbags/-handbags' in link_url:
      EmitUrl(link_url, CoachProcessCategoryPage)

  # Find all handbags and their information!
  for span in FindAllClass(soup, 'span', 'JSON'):
    try:
      code_str = span.contents[0].strip()
      code = json.loads(code_str)
    except ValueError, e:
      print "Error parsing JSON code:", e
      print "-" * 25
      print code_str
      print "-" * 25
      continue
    pp = handbag_pb2.PurchasePoint()
    pp.src_urls.append(url)
    pp.name = code['productName']
    pp.price = code['unitPrice']
    pp.breadcrumbs.append(code['categoryName'])
    # TODO(fedele): get rid of the leading and trailing "&amp;lt;li&amp;gt", etc
    descriptions = code['longDescription'].split('&lt;BR&gt;&amp;lt;li&amp;gt;')
    for description in descriptions:
      pp.descriptions.append(description)
    for swatch_dict in code['swatchGroup']['swatches']:
      pp.colors.append(swatch_dict['color'])
    script_txt = span.parent.script.contents[0].strip()
    magic_img_base = 'http://s7d2.scene7.com/is/image/Coach/' # Got this one by hand.
    img_relative_url = script_txt[script_txt.find('('):].split(',')[1].strip("'")
    img = pp.images.add()
    img.type = img.THUMBNAIL
    img.src = magic_img_base + img_relative_url
    Output(pp.name, pp)


def main(argv):
  repo = caches.OnDiskCacheStrategy('/tmp/grawlercache')
  seed_urls = ['http://www.coach.com/online/handbags/-handbags_features_newarrivals_1-10551-10051-5000000000000015027-en?t1Id=62&t2Id=5000000000000015027&tier=2']
  protokv_file_path = '/tmp/grawler-output2.kfv'
  grawler.RunGrawler(seed_urls, CoachProcessCategoryPage, repo,
                     protokv_file_path, handbag_pb2.PurchasePoint)


if __name__ == '__main__':
  app.run()
