from django.urls import path
from .views import ArticleViewSet

# ViewSet의 'list' 메서드를 GET 요청에 매핑
account_list = ArticleViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    path('article', account_list, name='article-list'),
]