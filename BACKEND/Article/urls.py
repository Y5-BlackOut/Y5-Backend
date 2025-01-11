from django.urls import path
from .views import *

# ViewSet의 'list' 메서드를 GET 요청에 매핑
news_list = NewsViewSet.as_view({
    'post': 'create',
    'get' : 'list',
})

blog_list = BlogPostViewSet.as_view({
    'post': 'create',
    'get': 'list',
})


detail_list = DetailView.as_view({
    'get': 'retrieve',
})

history_list = HistoryView.as_view({
    'get': 'retrieve',
})


urlpatterns = [
    path('news', news_list, name='article-list'),
    path('blog', blog_list, name="blog-list"),
    path('detail/<int:pk>/', detail_list, name='detail-list'),
    path('history/', history_list, name='history-list'),
]