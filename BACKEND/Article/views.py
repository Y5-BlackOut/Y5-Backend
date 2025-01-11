# from django.shortcuts import get_object_or_404
# from rest_framework.viewsets import ViewSet
# from rest_framework.response import Response
# from rest_framework import status
# from .models import News
# from .serializers import NewsSerializer
# import hashlib
# from NoditApi.service import *
# import json

# class NewsViewSet(ViewSet):

#     def create(self, request, *args, **kwargs):

#         # 요청 데이터에서 유저의 account private key 추출
#         ACCOUNT_PRIVATE_KEY = request.data.get('ACCOUNT_PRIVATE_KEY')

#         # 요청 데이터에서 해당 글의 reference id 리스트 추출
#         references = request.data.get('reference', [])  
        
#         # references에 해당하는 기존 데이터 조회
#         # 각 ID로 데이터 조회
#         related_news = []
#         for ref_id in references:
#             news = get_object_or_404(News, id=ref_id)  # 해당 ID의 객체 조회
#             related_news.append(news.transactionHash)

#         # test용
#         # print(related_news)

#         # Request 데이터에서 Serializer를 생성
#         serializer = NewsSerializer(data=request.data)
        
#         # 데이터 유효성 검사
#         if serializer.is_valid():

#             title = serializer.validated_data.get('title', '')
#             content = serializer.validated_data.get('content', '')
#             accountAddress = serializer.validated_data.get('accountAddress', '')

#             # print("!!!!")
#             # print(accountAddress)

#             # transactionHash 생성 
#             hash_input = f"{title}{content}{accountAddress}".encode()
#             integrityHash = hashlib.sha256(hash_input).hexdigest()

#             data = {"integrityHash" : integrityHash , "isNew" : True ,"references" : related_news, "oldVersion" : []}
#             dataToString = json.dumps(data, ensure_ascii=False)
#             createTransactionResult =  make_transactions(accountAddress, ACCOUNT_PRIVATE_KEY, dataToString)
#             transactionHash = createTransactionResult.get("transactionHash")
#             if not transactionHash:
#                 return Response({"error": "Failed to generate transaction hash"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#             serializer.save()  # 데이터 저장
#             return Response(serializer.data, status=status.HTTP_201_CREATED)  # 성공 응답
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 유효성 오류 응답
