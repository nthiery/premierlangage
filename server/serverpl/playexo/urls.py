 # coding: utf-8
 
from django.conf.urls import url

from . import views
from gitload.views import index

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^not_authenticated/.*$', views.not_authenticated),
    
    url(r'^activity/lti/(?P<activity_name>\w+)/(?P<strategy_name>\w+)/(?P<pltp_sha1>\w+)/$', views.lti_receiver),
    url(r'^activity/test/(?P<activity_name>\w+)/(?P<strategy_name>\w+)/(?P<pltp_sha1>\w+)/$', views.test_receiver),
    
    url(r'^activity/$', views.activity_view),
    
    url(r'^try/$', views.try_pl),
]


