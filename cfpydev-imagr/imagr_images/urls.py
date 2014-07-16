from django.conf.urls import patterns, url, include
from imagr_images import views

urlpatterns = patterns('',
    url(r'^(?P<album_id>\d+)/$', views.albumView, name='albums'),
    url(r'^photo/(?P<photo_id>\d+)/$', views.photoView, name='photo'),
    )
