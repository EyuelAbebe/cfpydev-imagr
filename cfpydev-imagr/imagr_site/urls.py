from django.conf.urls import patterns, include, url
from imagr_site import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from imagr_images import views as imageViews

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.front, name='front'),
    url(r'^home$', include('imagr_user.urls')),
    url(r'^album/', include('imagr_images.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^stream$', imageViews.streamView, name='stream'),
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
