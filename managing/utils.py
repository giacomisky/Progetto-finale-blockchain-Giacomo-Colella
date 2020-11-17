#from web3 import Web3


def sendTransaction(message):
    w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/d265c97f7731499084e370233e9f58c7'))
    address = '0x078E00f03FDC4946a1D4ebF96b1Bd951ef192fB0'
    privateKey = '0x5d6db1bf99d662e994323a53a62a7a3b9cab887c127df98c63634952a25286b6'
    nonce = w3.eth.getTransactionCount(address)
    gasPrice = w3.eth.gasPrice
    value = w3.toWei(0, 'ether')
    signedTx = w3.eth.account.signTransaction(dict(
        nonce=nonce,
        gasPrice=gasPrice,
        gas=100000,
        to='0x0000000000000000000000000000000000000000',
        value=value,
        data=str(message).encode('utf-8')
        ), privateKey)
    tx = w3.eth.sendRawTransaction(signedTx.rawTransaction)
    txId = w3.toHex(tx)
    return txId