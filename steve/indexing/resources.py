"""Definition of various Resource classes.

"""

import urllib
import hashlib


class PurchasePoint(object):
  def __init__(self, src_url, handbag_name, breadcrumbs, colors, price, images, details):
    self.src_url = src_url
    self.handbag_name = handbag_name
    self.breadcrumbs = breadcrumbs
    self.colors = colors
    self.price = price
    self.images = images
    self.details = details

  def CanonicalId(self):
    return hashlib.md5(self.handbag_name).hexdigest()

  def _PurchasePointTemplateString(self):
    """Return a template string - if you interpolate into it the color, you will
    get out an appropriate purchase_point string.
    """
    clean_src_url = urllib.quote_plus(self.src_url).replace('%', '%%')
    pp_vals = dict(price=self.price, source=clean_src_url, color="%s")
    return "purchase_point:%s" % ','.join("%s=%s" % (k, v) for (k, v) in pp_vals.iteritems())

  def WriteToOpenFile(self, f):
    print >> f, "tag:name=%s" % self.handbag_name
    tpl = self._PurchasePointTemplateString()
    for color in self.colors:
      print >> f, tpl % color
    for img in self.images:
      print >> f, "photo:url=%s" % urllib.quote_plus(img)
    for n, bc in enumerate(self.breadcrumbs):
      print >> f, "tag:type=breadcrumb,pos=%d,name=%s" % (n, bc)
    print >> f, "tag:type=details,name=%s" % repr(self.details)
