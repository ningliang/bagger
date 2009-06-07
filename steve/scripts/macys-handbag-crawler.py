"""One line description of module/program.

Longer, more detailed descrption.
"""


from cobra.steve.util.prelude import *
from cobra.steve.crawler import fetcher, caches
from cobra.steve.third_party.BeautifulSoup import *

import urlparse


def FindAllClass(soup, tag, class_rx):
  """Helper method that finds all tags with a class attribute that matches class_rx."""
  return soup.findAll(tag, attrs={'class': re.compile(class_rx)})


class Crawler(object):
  # TODO(fedele): move this class to cobra.steve.crawler

  def __init__(self, seed_urls):
    self.urls_seen = set()
    self.urls_to_process = []
    self._cur_url = None
    self.AddUrls(seed_urls)

  def AddUrls(self, urls):
    """Add multiple urls to be crawled."""
    map(self.AddUrl, urls)

  def AddUrl(self, url):
    """Add a single url to be crawled."""
    if url:
      full_url = urlparse.urljoin(self.CurrentUrl(), url)
      self.urls_to_process.append(full_url)

  def CurrentUrl(self):
      return self._cur_url

  def Run(self):
    """Runs the crawler.  Does not return until the entire
    crawl space has been explored.  As such, this may take awhile."""
    while self.urls_to_process:
      url = self.urls_to_process.pop(random.randint(0, len(self.urls_to_process) - 1))
      if url in self.urls_seen:
        continue
      self._cur_url = url
      print >> sys.stderr, "fetching [%-150s]..." % url[:150]
      self.urls_seen.add(url)
      data = fetcher.FetchUrl(url)
      soup = BeautifulSoup(data)
      self.Process(url, soup)

  def Process(self, url, soup):
    """If the given URL is fetched successfully, this method is called as
    a callback.  Implement application specific processing behavior here."""
    raise NotImplementedError



class MacysCrawler(Crawler):
  def Process(self, url, soup):
    if re.search(r'PageID=[0-9]+', url):
      self.ProcessCategoryPage(url, soup)
    else:
      detail_div = FindAllClass(soup, 'div', r'productDetailSection')
      if not detail_div:
        return
      assert len(detail_div) == 1
      self.ProcessDetailPage(url, soup, detail_div[0])

  def ProcessCategoryPage(self, url, soup):
    # For an "index" page:
    #   - every handbag link on the page (if this has multiple) X
    #   - the links to the next page (if paginated) X
    #   - the breadcrumbs on the page - eh...
    #   - links on the left (categories) but we want to avoid anything under the "accessories" thing  X
    #   - the thumbnail for each item (TODO)

    # Is there any pagination?  Add those as well!
    for a in FindAllClass(soup, 'a', 'depthPathLinked'):
      self.AddUrl(a.get('href', ''))

    # Add the category links on the left if necessary.
    for tr in soup.findAll('tr', attrs={'id': re.compile(r'menu_id_\d+_\d+')}):
      # TODO(fedele): right now we only want Macy's handbags, which at the moment
      # is menu_id_4 - restrict to those.
      if not tr['id'].startswith('menu_id_4'):
        continue
      self.AddUrl(tr.a.get('href', ''))

    # First, all handbags on the page:
    bags_found = 0
    for thumb_td in FindAllClass(soup, 'td', r'productThumb'):
      if not thumb_td.a:
        continue
      bags_found += 1
      href = thumb_td.a['href'].strip()
      img = thumb_td.a.img
      # print img
      img_src = img.get('src', '').strip()
      img_title = img.get('title', '').strip()
      img_alt = img.get('alt', '').strip()
      thumb_desc = FindAllClass(thumb_td, "div", 'productThumbDescContainer')[0]
      href2 = thumb_desc.a.get('href', '')
      h2_text = thumb_desc.h2.contents[0]
      price = thumb_desc.span.contents[0]
      # print h2_text, price
      assert href == href2
      self.AddUrl(href)
    pass

  def ProcessDetailPage(self, url, soup, detail_div):
    # For a "handbag" page:
    #   - the breadcrumbs  x
    #   - the descriptions x
    #   - details (dimensions, etc) x
    #   - colors
    #   - price x
    #   - images  (TODO)
    #   - reviews (TODO)
    breadcrumbs1 = soup.title.contents[0].split(' - ')
    breadcrumbs1.reverse()
    breadcrumb_div = FindAllClass(soup, 'div', 'breadCrumbs')[0]
    breadcrumbs2 = []
    for h in breadcrumb_div.findAll(re.compile(r'h[1-2]')):
      if h['class'] == 'depthPathLinked':
        h = h.a
      breadcrumbs2.append(h.contents[0])
    # We give preference to breadcrumbs2, e.g. the ones that don't appear in the title.
    breadcrumbs = breadcrumbs2

    short_detail = detail_div.h1.contents[0]
    long_detail = FindAllClass(detail_div, 'div', 'productDetailLong')[0].contents[0]
    print short_detail, long_detail

    details = [li.contents[0] for li in FindAllClass(detail_div, 'ul', 'prodInfoList')[0].findAll('li')]
    # TODO(fedele): extract webid, and dimensions
    price = FindAllClass(detail_div, 'span', 'productDetailPrice')[0].contents[0].strip()

    more_views_div = FindAllClass(soup, 'div', 'moreViews')[0]
    # TODO(fedele): ensure that this 
    big_images = [i['value'] for i in more_views_div.findAll('input')]

    colors = []
    color_select = soup.find('select', attrs={'id': 'color0'})
    if color_select:
      for opt in color_select.findAll('option'):
        if opt['value'] == "NOSELECTION":
          continue
        colors.append(opt['value'])
    print big_images, colors
      


def main(argv):
  random.seed(1337)
  seed_urls = ['http://www1.macys.com/catalog/index.ognc?CategoryID=27691&PageID=118933769578245&kw=Clutches %26 Occasion']
  crawler = MacysCrawler(seed_urls)
  crawler.Run()


if __name__ == '__main__':
  app.run()
