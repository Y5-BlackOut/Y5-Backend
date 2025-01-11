from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .service import get_transactions_by_account, get_input_by_hash
from requests.exceptions import HTTPError
from Article.models import *
import json


#account_address를 받아 해당 사용자의 모든 글을 반환합니다.
class ArticleViewSet(ViewSet):
    def list(self, request):

        # Query parameter로 account_address 가져오기
        account_address = request.query_params.get('account_address', None)
        type = request.query_params.get('type', None)

        if not account_address:
            return Response(
                {"error": "account_address is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # account address로 트랜잭션 데이터 가져오기
            transactionDict = get_transactions_by_account(account_address, "0", "latest")
        except HTTPError as e:
            # HTTPError 발생 시 401 Unauthorized 반환
            return Response(
                {"error": "Invalid account_address or unauthorized access"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # 기타 오류 발생 시 500 Internal Server Error 반환
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    
        result = {"account_address" : account_address, "data":[]}

        # 트랜잭션 해시별 글 데이터를 가져와 결과에 추가
        for i, transactionHash in transactionDict.items() :
            
            temp = {}

            article = ""

            if(type == "blog") :
                article = BlogPost.objects.filter(transactionHash=transactionHash).values('id', 'title', 'content','createdAt').first()
            
            else :
                article = News.objects.filter(transactionHash=transactionHash).values('id', 'title', 'content','createdAt').first()
            
            if(article == None) :
                continue
            
            input = get_input_by_hash(transactionHash)
            if input is not None :
                input_json = json.loads(input)
                reference = input_json.get('references')

            temp["id"] = article["id"]
            temp["title"] = article["title"]
            temp["content"] = article["content"]
            temp["createdAt"] = article["createdAt"]
            temp["reference"] = reference

            result["data"].append(temp)

        print(result)

        return Response(result, status=status.HTTP_200_OK)