from cobra.steve.util.prelude import *
from cobra.steve.crawler import fetcher
from cobra.steve.third_party.BeautifulSoup import *

import urlparse


URL_REGEXP = re.compile(r'/finance\?(q=(NYSE|NASDAQ):)|catid=[0-9]+')

def ExtractSymbols(soup):
		"""Extract all the symbols contained in the Google finance
		page contained in the given soup"""
		anchors = soup.findAll('a', href=URL_REGEXP)
		symbols = []
		for a in anchors:
				m = re.search(r'q=([A-Z]+):([A-Z]+)', a['href'])
				if not m:
						continue
				exchange, symbol = m.groups()
				symbols.append(symbol)
		return symbols


def ExtractCrawlUrls(base_url, soup):
		"""Extract all the next crawl urls contained in the given
		Google finance page's soup."""
		anchors = soup.findAll('a', href=URL_REGEXP)
		def Hostname(url):
				return urlparse.urlparse(url)[1]
		
		base_hostname = Hostname(base_url)
		crawl_urls = []
		for a in anchors:
				href = a.get('href', None)
				if 'catid' in a:
						print a
				if not href or href.startswith('?') or href.startswith('/group'):
						continue
				if 'catid' in a:
						print "YUP!"
				next_url = urlparse.urljoin(base_url, href)
				if Hostname(next_url) != base_hostname:
						continue
				crawl_urls.append(next_url)
		return crawl_urls


def main():
		cache_dir = '/tmp/crawlcache/gstock20090527'
		cache_strategy = fetcher.OnDiskCacheStrategy(cache_dir)
		output_file = open('data/symbols-google-finance-crawl-raw', 'w')
		urls = ['http://finance.google.com',
						"http://finance.google.com/finance?catid=57629812",
						"http://finance.google.com/finance?catid=53361227",
						"http://finance.google.com/finance?catid=59360336",
						"http://finance.google.com/finance?catid=57779728",
						"http://finance.google.com/finance?catid=52760568",
						"http://finance.google.com/finance?catid=60918252",
						"http://finance.google.com/finance?catid=58211593",
						"http://finance.google.com/finance?catid=64715132",
						"http://finance.google.com/finance?catid=54835206",
						"http://finance.google.com/finance?catid=66529330",
						"http://finance.google.com/finance?catid=57984048",
						"http://finance.google.com/finance?catid=54508229",
						]

		processed_urls = set()
		symbols_seen = set()
		while urls:
				# Randomly shuffle the URL set a bit.
				url = urls.pop(0)
				if url in processed_urls:
						continue
				processed_urls.add(url)
				print >> sys.stderr, "processing [%-60s]..." % url[:60],
				data = fetcher.FetchUrl(url, cache_strategy)
				soup = BeautifulSoup(data)
				symbols = ExtractSymbols(soup)
				new_symbols = 0
				for symbol in symbols:
						if symbol not in symbols_seen:
								print >> output_file, symbol
								new_symbols += 1
								symbols_seen.add(symbol)
				print >> sys.stderr, "%3d found, %3d new (%5d seen total)" % (len(symbols),
																																			new_symbols,
																																			len(symbols_seen))
				urls.extend(ExtractCrawlUrls(url, soup))
		pass


if __name__ == '__main__':
		main()
