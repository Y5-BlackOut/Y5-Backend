from django.db import models

# Create your models here.
class News(models.Model):
    title = models.CharField(max_length=255)  # 제목
    content = models.TextField()  # 내용
    accountAddress = models.CharField(max_length=255, null=True, blank=True)  
    transactionHash = models.CharField(max_length=255, unique=True, null=True, blank=True)    
    isLatest = models.BooleanField(default=True)  # 최신 여부
    createdAt = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updatedAt = models.DateTimeField(auto_now=True)  # 수정 시간

    class Meta:
        db_table = 'news'  # 테이블 이름 지정

    def __str__(self):
        return self.title

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    accountAddress = models.CharField(max_length=255, null=True, blank=True)  
    transactionHash = models.CharField(max_length=255, unique=True, null=True, blank=True)    
    isLatest = models.BooleanField(default=True)  # 최신 여부
    isLatest = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_post'  # 테이블 이름 명시적으로 설정 (선택 사항)

    def __str__(self):
        return self.title
