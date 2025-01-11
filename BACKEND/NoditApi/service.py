import requests
from dotenv import load_dotenv
import os
import binascii


# account에 들어있는 모든 transaction hash 값 시간 순으로 반환
def get_transactions_by_account(account_address, from_block, to_block):

    # 임시로 설정된 값값
    from_block = "0"
    to_block="latest"

    #NODIT_API_KEY 불러오기 
    load_dotenv()
    NODIT_API_KEY = os.getenv("NODIT_API_KEY")

    # url = "https://web3.nodit.io/v1/ethereum/mainnet/blockchain/getTransactionsByAccount"
    url = "https://web3.nodit.io/v1/ethereum/sepolia/blockchain/getTransactionsByAccount"


    headers = {
        "accept": "application/NODIT_API_KEYjson",
        "content-type": "application/json",
        "X-API-KEY": NODIT_API_KEY
    }

    payload = {
        "accountAddress": account_address,
        "fromBlock": from_block,
        "toBlock": to_block
    }

    # Make the API call
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx, 5xx)
    data = response.json()

    items = data.get("items", [])
    
    # Sort transactions by timestamp (descending order)
    sorted_items = sorted(items, key=lambda x: x["timestamp"], reverse=True)

    # Create a key-value dictionary (key: index, value: transactionHash)
    result = {i + 1: item["transactionHash"] for i, item in enumerate(sorted_items)}
    # print(result)

    return result
    # return data

def hex_to_utf8(hex_string):

    # 바이트로 변환
    byte_data = bytes.fromhex(hex_string[2:])

    # UTF-8로 디코딩
    utf8_string = byte_data.decode('utf-8')
    print(utf8_string)

    return utf8_string

# 각 transation hash로 input 내용 수집
def get_article_by_hash(transactionHash) :

    # NODIT_API_KEY 불러오기 
    load_dotenv()
    NODIT_API_KEY = os.getenv("NODIT_API_KEY")

    url = "https://web3.nodit.io/v1/ethereum/sepolia/blockchain/getTransactionByHash"

    payload = {
        "transactionHash": transactionHash,
        "withLogs": False,
        "withDecode": False
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": NODIT_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    # input만 반환
    data = response.json()
    input = data.get('input')

    # input 값 utf-8로 변환환
    return hex_to_utf8(input)
    
# get_article_by_hash("0xc5b1028dbcc1fa3286d1568201264b8abb6aa7b0142dedfc39bd332f8bc80773")