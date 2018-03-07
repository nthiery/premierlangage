 # coding: utf-8
 
from django.conf.urls import url

from classmanagement import views

urlpatterns = [
    url(r'^course/(\d+)/$', views.course_view),
    url(r'^course/(\d+)/student/(\d+)/summary/$', views.student_summary),
    url(r'^course/(\d+)/(\w+)/summary/$', views.activity_summary),
    url(r'^course/(\d+)/summary/$', views.course_summary),
    url(r'^course/(\d+)/correction/(\w+)/$', views.activity_correction),
    url(r'^redirect/(?P<activity_name>\w+)/$', views.redirect_activity),
    url(r'^cycle_color_blindness/$', views.cycle_color_blindness),
]

