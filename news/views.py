from django.views.generic.base import TemplateView

from news.models import NewsItem


class NewsItemView(TemplateView):
    template_name = 'news/item.html'

    def get_context_data(self, date, slug):
        context = super(NewsItemView, self).get_context_data()
        context['object'] = NewsItem.objects.get_by_url(date, slug)
        return context


class NewsFeedView(TemplateView):
    template_name = 'news/feed.html'

    def get_context_data(self, page=0):
        context = super(NewsFeedView, self).get_context_data()
        context['objects'] = NewsItem.objects.all()
        return context
