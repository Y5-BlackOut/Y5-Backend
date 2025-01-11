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
    

class DetailView(ViewSet):

    # 특정 id와 type (blog 또는 news)을 받아서 해당 글 반환
    def retrieve(self, request, pk=None):

        # Query parameter로 type 가져오기
        content_type = request.query_params.get('type', None)

        if not content_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 모델 선택 및 데이터 조회
        if content_type == "blog":
            model = BlogPost
            serializer_class = BlogPostSerializer
        elif content_type == "news":
            model = News
            serializer_class = NewsSerializer
        else:
            return Response(
                {"error": f"Invalid type '{content_type}', expected 'blog' or 'news'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # pk로 데이터 조회
        instance = get_object_or_404(model, pk=pk)

        # 직렬화
        serializer = serializer_class(instance)

        # transactionHash 값 가져오기
        transaction_hash = instance.transactionHash

        
        try:
            # transactionHash를 이용해 관련 데이터를 조회
            input = get_input_by_hash(transaction_hash)
            
            if input is not None:
                input_json = json.loads(input)  # JSON 문자열을 Python dict로 변환
                
                # references 값 가져오기
                reference = input_json.get('references', None)
                
                # oldVersion 값 가져오기 (없으면 None)
                old_version = input_json.get('oldVersion', None)



        except Exception as e:
            return Response(
                {"error": "Failed to process input data", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 응답 데이터 구성
        response_data = serializer.data  # 직렬화된 기본 데이터
        response_data['reference'] = reference  # 추가 데이터 포함
        response_data['old_version'] = old_version  # 추가 데이터 포함
        

        return Response(response_data, status=status.HTTP_200_OK)
    

class HistoryView(ViewSet):

    # transactionHash 받아서 글 반환환
    def retrieve(self, request, pk=None):

        # Query parameter로 type 가져오기
        transactionHash = request.query_params.get('transactionHash', None)

        if not transactionHash:
            return Response(
                {"error": "transactionHash parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # article 변수 초기화
        article = None

        # BlogPost 테이블에서 transactionHash로 조회
        try:
            article = BlogPost.objects.filter(transactionHash=transactionHash).first()
        except Exception as e:
            return Response(
                {"error": f"Error retrieving from BlogPost: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # News 테이블에서 transactionHash로 조회 (BlogPost에 값이 없을 경우)
        if article is None:
            try:
                article = News.objects.filter(transactionHash=transactionHash).first()
            except Exception as e:
                return Response(
                    {"error": f"Error retrieving from News: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # 조회된 article이 없을 경우
        if article is None:
            return Response(
                {"error": "No article found for the given transactionHash"},
                status=status.HTTP_404_NOT_FOUND
            )
        

         # 기본 데이터 구성
        response_data = {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "account_address" : article.accountAddress,
            "transactionHash": article.transactionHash,
            "isLatest": article.isLatest,
            "createdAt": article.createdAt,
            "updatedAt": article.updatedAt,
        }
        
        
        try:
            # transactionHash를 이용해 관련 데이터를 조회
            input = get_input_by_hash(transactionHash)
            
            if input is not None:
                input_json = json.loads(input)  # JSON 문자열을 Python dict로 변환
                
                # references 값 가져오기
                reference = input_json.get('references', None)
                
                # oldVersion 값 가져오기 (없으면 None)
                old_version = input_json.get('oldVersion', None)

        except Exception as e:
            return Response(
                {"error": "Failed to process input data", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 응답 데이터 구성
        response_data['reference'] = reference  # 추가 데이터 포함
        response_data['old_version'] = old_version  # 추가 데이터 포함
        

        return Response(response_data, status=status.HTTP_200_OK)

    