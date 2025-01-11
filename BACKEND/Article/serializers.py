from rest_framework import serializers
from .models import News, BlogPost

class NewsSerializer(serializers.ModelSerializer):
    transactionHash = serializers.CharField(required=False)  # transactionHash 필드 생략 가능

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'accountAddress','transactionHash', 'isLatest', 'createdAt', 'updatedAt']

class BlogPostSerializer(serializers.ModelSerializer):
    transactionHash = serializers.CharField(required=False)  # transactionHash 필드 생략 가능

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'accountAddress','transactionHash', 'isLatest', 'createdAt', 'updatedAt']
