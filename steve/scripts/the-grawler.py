from cobra.steve.util.prelude import *
from cobra.steve.crawler import grawler, caches
from cobra.steve.indexing.proto import handbag_pb2
from cobra.steve.indexing import protokv


def FindAllClass(soup, tag, class_rx):
  """Helper method that finds all tags with a class attribute that matches class_rx."""
  return soup.findAll(tag, attrs={'class': re.compile(class_rx)})


def MacysProcessCategoryPage(url, soup, EmitUrl, Output):
  # Is there any pagination?  Add those as well!
  for a in FindAllClass(soup, 'a', 'depthPathLinked'):
    EmitUrl(a.get('href', ''), MacysProcessCategoryPage)

  # Add the category links on the left if necessary.
  for tr in soup.findAll('tr', attrs={'id': re.compile(r'menu_id_\d+_\d+')}):
    # TODO(fedele): right now we only want Macy's handbags, which at the moment
    # is menu_id_4 - restrict to those.
    if not tr['id'].startswith('menu_id_4'):
      continue
    EmitUrl(tr.a.get('href', ''), MacysProcessCategoryPage)

  # Find all handbags on the page:
  for thumb_td in FindAllClass(soup, 'td', r'productThumb'):
    if not thumb_td.a:
      continue
    pp = handbag_pb2.PurchasePoint()
    pp.src_urls.append(url)
    thumb_desc = FindAllClass(thumb_td, "div", 'productThumbDescContainer')[0]
    pp.price = str(thumb_desc.span.contents[0])
    pp.name = thumb_desc.h2.contents[0]
    # These links should be the same - fortunately the url crawler should de-dup them.
    EmitUrl(thumb_desc.a.get('href', ''), MacysProcessDetailPage, pp.name)
    EmitUrl(thumb_td.a['href'].strip(), MacysProcessDetailPage, pp.name)
    # Extract the thumbnail (which has copious amounts of info on it)
    img = thumb_td.a.img
    img_pb = pp.images.add()
    img_pb.type = img_pb.THUMBNAIL
    img_pb.src = img.get('src', '').strip()
    img_pb.title = img.get('title', '').strip()
    img_pb.alt_text = img.get('alt', '').strip()
    Output(pp.name, pp)


def MacysProcessDetailPage(url, soup, EmitUrl, Output,
                           bag_title):
  # Make sure the page is valid for what we're looking for.
  detail_div = FindAllClass(soup, 'div', r'productDetailSection')[0]
  if not detail_div:
    return

  pp = handbag_pb2.PurchasePoint()
  pp.src_urls.append(url)

  # Breadcrumbs!
  breadcrumb_div = FindAllClass(soup, 'div', 'breadCrumbs')[0]
  for h in breadcrumb_div.findAll(re.compile(r'h[1-2]')):
    if h['class'] == 'depthPathLinked':
      h = h.a
    pp.breadcrumbs.append(h.contents[0])

  # Item details.
  # TODO(fedele): extract dimensions here.
  short_detail = FindAllClass(detail_div, 'h1', 'productDetailShort')[0].contents[0]
  long_detail = FindAllClass(detail_div, 'div', 'productDetailLong')[0].contents[0]
  pp.summary = "%s\n\n%s" % (short_detail, long_detail)
  for li in FindAllClass(detail_div, 'ul', 'prodInfoList')[0].findAll('li'):
    pp.descriptions.append(li.contents[0])

  # Price.
  pp.price = FindAllClass(detail_div, 'span', 'productDetailPrice')[0].contents[0].strip()
    
  # Extract any big images that we can find.
  more_views_div = FindAllClass(soup, 'div', 'moreViews')
  if more_views_div:
    for imput in more_views_div[0].findAll('input'):
      img_pb = pp.images.add()
      img_pb.src = imput['value']

  # Extract colors.
  color_select = soup.find('select', attrs={'id': 'color0'})
  if color_select:
    for opt in color_select.findAll('option'):
      if opt['value'] == "NOSELECTION":
        continue
      pp.colors.append(opt['value'])

  # And finally output the mess.
  Output(bag_title, pp)


def main(argv):
  repo = caches.OnDiskCacheStrategy('/tmp/grawlercache')
  seed_urls = ['http://www1.macys.com/catalog/index.ognc?CategoryID=27691&PageID=118933769578245&kw=Clutches %26 Occasion']
  protokv_file_path = '/tmp/grawler-output.kfv'
  grawler.RunGrawler(seed_urls, MacysProcessCategoryPage, repo,
                     protokv_file_path, handbag_pb2.PurchasePoint)


if __name__ == '__main__':
  app.run()
