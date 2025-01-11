from django.contrib import admin
from .models import News, BlogPost

# 모델 등록
admin.site.register(News)
admin.site.register(BlogPost)

