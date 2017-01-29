from django.conf.urls import include, url


urlpatterns = [
    url(r'^news/', include('news.urls')),
    url(r'', include('dc17.urls')),
    url(r'', include('wafer.urls')),
]
