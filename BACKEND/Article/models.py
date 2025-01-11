from django.db import models

# Create your models here.
class Article(models.Model):
    BLOG = 'BLOG'
    NEWS = 'NEWS'

    ARTICLE_TYPES = [
        (BLOG, 'Blog'),
        (NEWS, 'News'),
    ]

    title = models.CharField(max_length=255) # 글 제목
    content = models.TextField() # 글 내용
    author = models.CharField(max_length=100) # 작성자
    transactionHash = models.CharField(max_length=255) # transactionHash 값
    type = models.CharField( # 글의 종류                           
        max_length=10,
        choices=ARTICLE_TYPES,
        default=BLOG,  # 기본값은 BLOG
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)      # 수정 시간

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"
