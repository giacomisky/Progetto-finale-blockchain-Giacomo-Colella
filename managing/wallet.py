from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/d265c97f7731499084e370233e9f58c7"))
account = w3.eth.account.create()
privateKey = account.privateKey.hex()
address = account.address

print(address+' e '+privateKey)
