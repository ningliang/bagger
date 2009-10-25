# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection, transaction
from django.shortcuts import render_to_response
from django import forms
from django.conf import settings

from handbags.bags.models import Handbag, Rating

import random
import os.path
import mimetypes
from operator import itemgetter
from itertools import *


class RatingForm(forms.Form):
  rating = forms.TypedChoiceField(choices=[('1', '1 (worst)'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5 (best)')], coerce=int)
  reason = forms.CharField(label='Reason (optional)', required=False)

  
def GetUserId(request):
  if not 'user_id' in request.session:
    user_id = "U%08d" % random.randint(0, 10 ** 8 - 1)
    request.session['user_id'] = user_id
  else:
    user_id = request.session['user_id']
  return user_id

    
def rate_specific(request, bag_id):
  user_id = GetUserId(request)
  bag = Handbag.objects.get(id=bag_id)
  if request.method == 'POST':
    form = RatingForm(request.POST)
    if form.is_valid():
      Rating.objects.create(handbag=bag, user=user_id, rating=form.cleaned_data['rating'], reason=form.cleaned_data['reason'])
      return HttpResponseRedirect('/rate/random/')
  else:
    form = RatingForm()      
  tpldict = {'bag': bag, 'form': form, 'user_id': user_id}
  return render_to_response("bags/rate_bag.html", tpldict)
  

def serve_image(request, bag_id):
  bag = Handbag.objects.get(id=bag_id)
  fullpath = os.path.join(settings.IMAGES_DIRECTORY, bag.original_image_path)
  mimetype, encoding = mimetypes.guess_type(fullpath)
  data = open(fullpath, 'rb').read()
  return HttpResponse(data, mimetype=mimetype)
  
  
def serve_thumbnail_image(request, bag_id):
  bag = Handbag.objects.get(id=bag_id)
  fullpath = os.path.join(settings.IMAGES_DIRECTORY, bag.original_image_path)
  thumbnail_filepath = thumbnail(fullpath)  
  mimetype, encoding = mimetypes.guess_type(thumbnail_filepath)
  data = open(thumbnail_filepath, 'rb').read()
  return HttpResponse(data, mimetype=mimetype)
  
  

def rate_random(request):
  user_id = GetUserId(request)
  c = connection.cursor()
  already_rated = [r.handbag.id for r in Rating.objects.filter(user=user_id)]
  if already_rated:
    where_clause = ' where id not in (%s)' % ','.join(imap(str, already_rated))
  else:
    where_clause = ''
  c.execute('select id from bags_handbag' + where_clause)
  bag_ids = map(itemgetter(0), c.fetchall())
  if bag_ids:
    random_id = random.choice(bag_ids)
    return HttpResponseRedirect("/rate/%s/" % random_id)
  else:
    return HttpResponse("wow, you're awesome - you've already rated them all!  come back later")
    
    
from PIL import Image
import os.path
import StringIO

def thumbnail(filename, size=(50, 50), output_filename=None):
  image = Image.open(filename)
  if image.mode not in ('L', 'RGB'):
    image = image.convert('RGB')
  image = image.resize(size, Image.ANTIALIAS)

  # get the thumbnail data in memory.
  if not output_filename:
    output_filename = get_default_thumbnail_filename(filename)
  image.save(output_filename, image.format) 
  return output_filename

  
def thumbnail_string(buf, size=(50, 50)):
  f = StringIO.StringIO(buf)
  image = Image.open(f)
  if image.mode not in ('L', 'RGB'):
    image = image.convert('RGB')
  image = image.resize(size, Image.ANTIALIAS)
  o = StringIO.StringIO()
  image.save(o, "JPEG")
  return o.getvalue()

    
def get_default_thumbnail_filename(filename):
  path, ext = os.path.splitext(filename)
  return path + '.thumb.jpg'
   
