# Create your views here.
from django.views.generic import list_detail
from django.http import HttpResponse
from django.shortcuts import render_to_response


def search(request, queryset, **kwargs):
  default_args = dict(paginate_by=5)
  default_args.update(kwargs)
  # OK, i'd like to start searching now... the question is, what do
  # we do this on?  Unfortunately our handbag representation is a bit...
  # sparse.  We might want to be able to search on _tags_ - if these things
  # had them.
  # in fact, just doing tag based search may in fact be easier... we can
  # define collections of tags 
  return list_detail.object_list(request, queryset, **default_args)