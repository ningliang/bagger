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
    getPage(url).addCallbacks(callback, errback=multiplexer.Errback)
  

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
    yield Plex("http://www.google.com", self.GenericProcess)
    
  def GenericProcess(self, url, value):
    println(value)
    
  def ProcessHistoricalData(self, url, value):
    pass
    
  def ProcessGoogleStockSummary(self, url, value):
    pass
    
  def ProcessGoogleFinancialsPage(self, url, sheet_type, period_type, value):
    pass
    
  def ProcessEdgarIndexPage(self, url, value, page_num=1):
    pass

  def ProcessEdgarMidularPage(self, url, report_name, report_date, value):
    pass
    
  def ProcessEdgarReportPage(self, url, report_name, report_something):
    pass
    
# TODO(fedele): figure out how to feed urls back into this system


  
    

  

if __name__ == '__main__':
  app.run()