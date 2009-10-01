from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
  # Example:
  (r'^rate/random/$', 'handbags.bags.views.rate_random'),
  (r'^rate/(\d+)/$', 'handbags.bags.views.rate_specific'),
  (r'^img/(\d+)/$', 'handbags.bags.views.serve_image'),

  # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
  # to INSTALLED_APPS to enable admin documentation:
  # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

  # Uncomment the next line to enable the admin:
  # (r'^admin/', include(admin.site.urls)),
)