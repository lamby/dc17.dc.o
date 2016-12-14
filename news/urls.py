from django.conf.urls import url

from news.views import NewsItemView, NewsFeedView


urlpatterns = [
    url(r'^(?:page/(?P<page>[0-9]+)/)?$',
        NewsFeedView.as_view(), name='news'),
    url(r'^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})-(?P<slug>[^/]+)/$',
        NewsItemView.as_view(), name='news_item'),
]
