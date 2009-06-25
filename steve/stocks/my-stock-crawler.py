from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.python.util import println


from cobra.steve.util.prelude import *


def main(argv):
  stocks = ['NAT', 'GOOG', 'OSK', 'CMG', 'FRO']
  for stock in stocks:
    DoFetchTickerSymbol(stock)
  reactor.run()


def DoFetchTickerSymbol(ticker_symbol):
  multiplexer = TickerUrlMultiplexer()
  for url, callback in multiplexer.Multiplex(ticker_symbol):
    foo = getPage(url).addCallbacks(callback, errback=multiplexer.Errback)
    print "FOO", foo
  print "DONE", ticker_symbol


class TickerUrlMultiplexer(object):
  def __init__(self):
    pass

  def Errback(self, error):
    println("an error occurred", error)

  def Multiplex(self, ticker_symbol):
    # Get historical data
    # Get stock summary (google page) (similar companies, sectors, key ratios, company description)
    # Get quarterly/annual numbers from google finance
    # Get all annual reports (10-K, 10-F, ANS, etc...) for as many years as possible
    def Plex(url, callback):
      return url, partial(callback, url)

    yield Plex("http://www.google.com/finance?q=%s" % ticker_symbol,
               self.ProcessGoogleStockSummary)
    yield Plex("http://www.google.com/finance/historical?q=%s&startdate=Jan+1,+1985&enddate=Jun+25,+2009&output=csv" % ticker_symbol,
               self.ProcessHistoricalData)
    yield Plex("http://www.google.com/finance?fstype=ii&q=%s" % ticker_symbol,
               self.ProcessGoogleFinancialsPage)
    yield Plex("http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&match=&CIK=SFL&filenum=&State=&SIC=&owner=include&",
               self.ProcessEdgarIndexPage)
    yield Plex("http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001289877&type=&dateb=&owner=include&start=40&count=40",
               partial(self.ProcessEdgarIndexPage, page_num=2))

  def ProcessHistoricalData(self, url, value):
    print "GOT", url, len(value)
    print value[:250]

  def ProcessGoogleStockSummary(self, url, value):
    # Get related companies, sector, industry
    print "GOT", url, len(value)

  def ProcessGoogleFinancialsPage(self, url, value):
    # Google actually serves all 6 tables in one result - its easy for us to extract them here.
    print "GOT", url, len(value)
    pass

  def ProcessEdgarIndexPage(self, url, value, page_num=1):
    # Identify if there is a next page and, if so, crawl it.
    # Output Item, formats, description, filed/effective
    print "GOT", url, len(value)
    pass

  def ProcessEdgarMidularPage(self, url, report_name, report_date, value):
    pass

  def ProcessEdgarReportPage(self, url, report_name, report_something):
    pass

# TODO(fedele): figure out how to feed urls back into this system
# OK, so how to do this?  Well, I think the model should be something as follows:
#
# We write a crawler as a bunch of methods, and string them together with callbacks
# We write a simple crawler that caches the resulting HTML result locally - in this
# way we can ensure that running it multiple times is fast.




if __name__ == '__main__':
  app.run()
