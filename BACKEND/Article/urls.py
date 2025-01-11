from django.urls import path
from .views import *

# ViewSet의 'list' 메서드를 GET 요청에 매핑
news_list = NewsViewSet.as_view({
    'post': 'create',
})

urlpatterns = [
    path('news', news_list, name='article-list'),
]