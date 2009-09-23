from django.db import models
from django.conf import settings

import os.path


class Handbag(models.Model):
  # The name of the bag, e.g. "Stone Mountain Splendor Two Top Zip"
  name = models.CharField(max_length=200)

  # The bag type, e.g. "hobo", "clutch", "evening", "satchel".
  # This is usually just the category 
  bag_type = models.CharField(max_length=30, blank=True, null=True)
  
  # The colors this bag is available in, separated by spaces.  There  
  # should be a space at the start and end of the string, so that a
  # SQL LIKE lookup of "% red %" will return red and only red bags.
  # This is to avoid matching simply on LIKE "%red%" and then getting
  # substring matches like "colored".

  # TODO(fedele): make this a better model (e.g. another table?)
  colors = models.CharField(max_length=250, blank=True, null=True)
  
  # The brand of the bag, e.g. "Coach", "Fossil"
  brand = models.CharField(max_length=75, blank=True, null=True)
  
  # How much the bag is, in USD - e.g. $102.99.  Eight digits with
  # 2 decimal places allow for prices up to $999,999.99 - we won't
  # be able to handle million dollar bags.  
  price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
  
  # A link to the bag specification page, e.g. "http://www1.macys.com/catalog/product/index.ognc?ID=432035&CategoryID=46020"
  link = models.URLField(verify_exists=False, max_length=400)
  
  # The local paths of the thumbnail and fullsize images.  These should be normalized
  # by the output of the crawler pipeline to be specific sizes, and should be named
  # "fullXXXXXX.jpg" and "thumbXXXXXX.jpg" respectively, where XXXX is the associated
  # handbag's ID.
  original_image_path = models.FilePathField(path=settings.IMAGES_DIRECTORY, match='orig', blank=True, null=True)
  fullsize_image_path = models.FilePathField(path=settings.IMAGES_DIRECTORY, match='full', blank=True, null=True)
  thumbnail_image_path = models.FilePathField(path=settings.IMAGES_DIRECTORY, match='thumb', blank=True, null=True)
  
  # Any extra information about the bag, such as a full length product description,
  # and possibly itemized lists of information.
  description = models.TextField(blank=True, null=True)


class Rating(models.Model):
  handbag = models.ForeignKey(Handbag)
  user = models.CharField(max_length=10)
  rating = models.PositiveSmallIntegerField()  
  reason = models.TextField(blank=True, null=True)