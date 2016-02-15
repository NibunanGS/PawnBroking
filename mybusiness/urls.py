from django.conf.urls import patterns, include, url

import autocomplete_light
from pawnbroking import auction_views
# from pawnbroking import views
autocomplete_light.autodiscover()


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mybusiness.views.home', name='home'),
    # url(r'^mybusiness/', include('mybusiness.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
#     url(r'^admin/auctionnotice/view_pledges', include(admin.site.urls)),
    url(r'^pawnbroking/get_pledges_for_auction/$', auction_views.get_pledges_for_auction, name='get_pledges_for_auction'),
    url(r'^pawnbroking/save_customer_address/$', auction_views.save_customer_address, name='save_customer_address'),
    url(r'^pawnbroking/generate_auction_notice/$', auction_views.generate_auction_notice, name='generate_auction_notice'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    
)
