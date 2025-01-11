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
        # isLatest가 True인 데이터만 필터링, 가장 최신 글만 제공공
        news = News.objects.filter(isLatest=True)
        
        # 직렬화 및 응답 반환
        serializer = NewsSerializer(news, many=True)
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
        # isLatest가 True인 데이터만 필터링, 가장 최신 글만 제공공
        blogs = BlogPost.objects.filter(isLatest=True)
        
        # 직렬화 및 응답 반환
        serializer = BlogPostSerializer(blogs, many=True)
        return Response(serializer.data)


class UpdateViewSet(ViewSet):
        
    def create(self, request, *args, **kwargs):

        # 요청 데이터에서 유저의 account private key 추출
        ACCOUNT_PRIVATE_KEY = request.data.get('ACCOUNT_PRIVATE_KEY')

        # 요청 데이터에서 id와 type 추출
        item_id = request.data.get('id', None)  # id 값 가져오기
        content_type = request.data.get('type', None)  # type 값 가져오기
        title = request.data.get('title', None)
        content = request.data.get('content', None)
        accountAddress = request.data.get('account_address', None)

        # id와 type 검증
        if not item_id:
            return Response(
                {"error": "id is required in the request body"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not content_type:
            return Response(
                {"error": "type is required in the request body"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 처리 로직 작성 (예: 모델 조회)
        if content_type == "blog":
            model = BlogPost
        else:
            model = News

        # id로 해당 객체 조회
        instance = model.objects.filter(id=item_id).first()

        if not instance:
            return Response(
                {"error": f"No {content_type} found with id {item_id}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 수정 전 글의 isLatest 값을 False로 업데이트
        instance.isLatest = False
        instance.save()  # 변경사항 저장
        
        # 수정 전 transactionHash 값 추출
        oldTransactionHash = instance.transactionHash

        try:
            # transactionHash를 이용해 관련 데이터를 조회
            input = get_input_by_hash(oldTransactionHash)
            
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

        # 기존 버전을 old_version 목록에 추가
        old_version.append(oldTransactionHash) # type 확인 필요 

        # 수정된 글에 대한 integrityHash 및 transactionHash 생성 
        hash_input = f"{title}{content}{accountAddress}".encode()
        integrityHash = hashlib.sha256(hash_input).hexdigest()

        data = {
            "integrityHash" : integrityHash, 
            "isNew" : False,
            "references" : reference, 
            "oldVersion" : old_version
        }
        dataToString = json.dumps(data, ensure_ascii=False)

        # 일기 수정에 대한 transaction 생성
        createTransactionResult = make_transactions(accountAddress, ACCOUNT_PRIVATE_KEY, dataToString)
        print(createTransactionResult)
        transactionHash = createTransactionResult.get("transactionHash")



        # 수정에 대한 새로운 데이터 생성
        new_instance = model.objects.create(
            title=title,
            content=content,
            transactionHash=transactionHash,
            isLatest=True,  # 새로 생성된 데이터는 최신 데이터로 설정
            accountAddress=accountAddress,
        )

        # 응답 데이터 구성
        response_data = {
            "id": new_instance.id,
            "title": new_instance.title,
            "content": new_instance.content,
            "account_address": new_instance.accountAddress,
            "transactionHash": new_instance.transactionHash,
            "isLatest": new_instance.isLatest,
            "createdAt": new_instance.createdAt,
            "updatedAt": new_instance.updatedAt,
            "references": reference,
            "old_version": old_version,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)




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

    # transactionHash 받아서 글 반환
    def retrieve(self, request, pk=None):

        # Request Body에서 transactionHash 가져오기
        transactionHash = request.query_params.get('transactionHash', None)

        if not transactionHash:
            return Response(
                {"error": "transactionHash body is required"},
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
    



    