import requests
from dotenv import load_dotenv
import os

def get_transactions_by_account(account_address, from_block, to_block):

    # 임시로 설정된 값값
    from_block = "19415000"
    to_block="latest"

    #NODIT_API_KEY 불러오기 
    load_dotenv()
    NODIT_API_KEY = os.getenv("NODIT_API_KEY")

    url = "https://web3.nodit.io/v1/ethereum/mainnet/blockchain/getTransactionsByAccount"
    
    
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
    return response.json()


def GetTransactionsByHash(transactionHash) :


    #NODIT_API_KEY 불러오기 
    load_dotenv()
    NODIT_API_KEY = os.getenv("NODIT_API_KEY")

    url = "https://web3.nodit.io/v1/ethereum/mainnet/blockchain/getBlockByHashOrNumber"

    payload = { "block": transactionHash }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": NODIT_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

    return response.json()  # JSON 형식의 응답 반환


# def GetInputByTransacion(blockInfo) :

