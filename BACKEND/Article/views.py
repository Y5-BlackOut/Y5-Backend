from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import News, BlogPost
from .serializers import NewsSerializer, BlogPostSerializer
import hashlib
from NoditApi.service import *
import json

class NewsViewSet(ViewSet):

    def create(self, request, *args, **kwargs):

        # 요청 데이터에서 유저의 account private key 추출
        ACCOUNT_PRIVATE_KEY = request.data.get('ACCOUNT_PRIVATE_KEY')
        # print(ACCOUNT_PRIVATE_KEY)

        # 요청 데이터에서 해당 글의 reference id 리스트 추출
        references = request.data.get('reference', [])  
        
        # Request 데이터에서 Serializer를 생성
        serializer = NewsSerializer(data=request.data)
        
        # 데이터 유효성 검사
        if serializer.is_valid():

            title = serializer.validated_data.get('title', '')
            content = serializer.validated_data.get('content', '')
            accountAddress = serializer.validated_data.get('accountAddress', '')

            # transactionHash 생성 
            hash_input = f"{title}{content}{accountAddress}".encode()
            integrityHash = hashlib.sha256(hash_input).hexdigest()

            data = {
                "integrityHash" : integrityHash, 
                "isNew" : True,
                "references" : references, 
                "oldVersion" : []
            }
            dataToString = json.dumps(data, ensure_ascii=False)

            # 일기 생성에 대한 transaction 생성
            createTransactionResult = make_transactions(accountAddress, ACCOUNT_PRIVATE_KEY, dataToString)
            transactionHash = createTransactionResult.get("transactionHash")
            
            print(transactionHash)
            
            if not transactionHash:
                return Response({"error": "Failed to generate transaction hash"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 데이터 저장
            instance = serializer.save(transactionHash=transactionHash)
            return Response(NewsSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 유효성 오류 응답
    
    def list(self, request):
        """모든 BlogPost 글을 조회"""
        blogs = News.objects.all()
        serializer = NewsSerializer(blogs, many=True)
        return Response(serializer.data)
    


class BlogPostViewSet(ViewSet):

    def create(self, request, *args, **kwargs):

        # 요청 데이터에서 유저의 account private key 추출
        ACCOUNT_PRIVATE_KEY = request.data.get('ACCOUNT_PRIVATE_KEY')
        # print(ACCOUNT_PRIVATE_KEY)

        # 요청 데이터에서 해당 글의 reference id 리스트 추출
        references = request.data.get('reference', [])  
        
        # Request 데이터에서 Serializer를 생성
        serializer = BlogPostSerializer(data=request.data)
        
        # 데이터 유효성 검사
        if serializer.is_valid():

            title = serializer.validated_data.get('title', '')
            content = serializer.validated_data.get('content', '')
            accountAddress = serializer.validated_data.get('accountAddress', '')

            # transactionHash 생성 
            hash_input = f"{title}{content}{accountAddress}".encode()
            integrityHash = hashlib.sha256(hash_input).hexdigest()

            data = {
                "integrityHash" : integrityHash, 
                "isNew" : True,
                "references" : references, 
                "oldVersion" : []
            }
            dataToString = json.dumps(data, ensure_ascii=False)

            # 일기 생성에 대한 transaction 생성
            createTransactionResult = make_transactions(accountAddress, ACCOUNT_PRIVATE_KEY, dataToString)
            transactionHash = createTransactionResult.get("transactionHash")
            
            print(transactionHash)
            
            if not transactionHash:
                return Response({"error": "Failed to generate transaction hash"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 데이터 저장
            instance = serializer.save(transactionHash=transactionHash)
            return Response(BlogPostSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 유효성 오류 응답



    def list(self, request):
        """모든 BlogPost 글을 조회"""
        blogs = BlogPost.objects.all()
        serializer = BlogPostSerializer(blogs, many=True)
        return Response(serializer.data)
    

    def retrieve(self, request, pk=None):
        """특정 id로 BlogPost 글 조회"""
        try:
            blog = BlogPost.objects.get(pk=pk)
            serializer = BlogPostSerializer(blog)
            return Response(serializer.data)
        except BlogPost.DoesNotExist:
            return Response({"error": "Blog not found"}, status=404)