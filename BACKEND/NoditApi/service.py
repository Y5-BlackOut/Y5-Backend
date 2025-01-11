import requests
from dotenv import load_dotenv
import os
import binascii
from web3 import Web3


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

    # print("!!!!!!!")
    # print(hex_string)

    try :
        # 바이트로 변환
        byte_data = bytes.fromhex(hex_string[2:])

        # UTF-8로 디코딩
        utf8_string = byte_data.decode('utf-8')
        # print(utf8_string)

    except ValueError as e:
        # 입력이 유효한 16진수가 아닌 경우
        print(f"Invalid hex input: {input}")
        raise ValueError("Invalid hexadecimal input.") from e

    except UnicodeDecodeError as e:
        # UTF-8로 디코딩 실패
        print(f"Failed to decode input as UTF-8: {input}")
        raise ValueError("Input cannot be decoded as UTF-8.") from e

    return utf8_string

# 각 transation hash로 input 내용 수집
def get_input_by_hash(transactionHash) :

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
    if(data.get('from') == data.get('to')) :
        input = data.get('input')
        return hex_to_utf8(input)

    return


def make_transactions(account_address, account_private_key, data):
    try:
        RPC_URL = "https://ethereum-sepolia.nodit.io/Gp0BX6eArEipGoSFq2fN4CH3T0yVpy_q"
        web3 = Web3(Web3.HTTPProvider(RPC_URL))
    
        nonce = web3.eth.get_transaction_count(account_address)

        tx = {
            'nonce': nonce,
            'to': account_address,  # 송신자와 수신자 동일
            'value': web3.to_wei(0.01, 'ether'),  # 전송할 Ether 양
            'gas': 40000,  # 기본 가스 한도
            'gasPrice': web3.to_wei('50', 'gwei'),  # 가스 가격
            'chainId': 11155111,  # Sepolia 체인 ID
            'data': web3.to_hex(text=data) #우리 넣을 데이터 여기 들어갈 예정 텍스트가 아니면 이따가 수정해야 돼
        }

        # 트랜잭션 서명
        signed_tx = web3.eth.account.sign_transaction(tx, account_private_key)

        # 트랜잭션 전송
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # 트랜잭션 해시 반환
        return {"transactionHash": web3.to_hex(tx_hash)}

    except ValueError as ve:
        return {"error": f"트랜잭션 서명 오류: {str(ve)}"}
    except Exception as e:
        return {"error": f"트랜잭션 전송 오류: {str(e)}"}
    
    

# account_address = "0x13F86F941942E1919e3C92A1Cf1Ba4e2d13FE1Cd"
# account_private_key = "edc827b83ea62038f702902a2226df66ca4f99234da0ea498ec1eb57c6214d50"
# hash = make_transactions(account_address, account_private_key, "datadatadata")
# print(hash)