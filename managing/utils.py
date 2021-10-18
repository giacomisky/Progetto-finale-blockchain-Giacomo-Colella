from hashlib import sha256
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))
import json


def sendTransaction(message):
    account = "0x7478Ee1125490E3fD8eCCBF9860c749174103247"
    privateKey = "923142d6c650d92df94f690ff57364ec13803f7d6bb88161a721abf5a07a265f"
    
    nonce = w3.eth.getTransactionCount(account)
    gasPrice = w3.eth.gasPrice
    value = w3.toWei(0, 'ether')
    signedTx = w3.eth.account.signTransaction(dict(
        nonce=nonce,
        gasPrice=gasPrice,
        gas=100000,
        to='0x0000000000000000000000000000000000000000',
        value=value,
        data=message.encode('utf-8'),
        ), privateKey)
    tx = w3.eth.sendRawTransaction(signedTx.rawTransaction)
    txId = w3.toHex(tx)
    return txId


def createWallet(password):
    account = w3.eth.account.create()
    balance = w3.eth.getBalance(account.address)
    print(account)
    cryptKey = account.encrypt(password)

    wallData = {
        'address': account.address,
        'balance': balance,
        'cryptKey': cryptKey
    }
        
    return wallData


def decryptWalKey(cryptKey, psw):
    print('we')
    myKey = w3.eth.account.decrypt(cryptKey, psw)
    print(myKey)
    return myKey