from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User
import redis
import json
from user.models import Auct, Storage, Wallet
from .utils import *

client = redis.StrictRedis(host='127.0.0.1', port=6379, password='',db=0)

#Add this auction on Redis
def addAuction(auctionId):  
    dettAuct = Auct.objects.filter(id=auctionId).values()
    thisAuct = dettAuct[0]
    client.lpush(f"Auction{thisAuct['id']}", f"Starting price: {thisAuct['price']} euro")


#update the work-flow list on Redis
def tip(identif, pricef, userf, date):
    client.rpush(f"Auction{identif}", f"{userf} has offered {pricef} | {date}")
    client.rpush("workflow", f"{userf} has offered {pricef} euro on Auction{identif}")


#The result is permanently saved on Sqlite and Ropsten(Json)
def permanentSaving(auction, winner): 
    winn = User.objects.filter(username=winner).values()[0]
    client.rpush("workflow", f"{winn['username']} has win the auction{auction.id}")

    #Replay the bets on SQLite
    lista = client.lrange(f"Auction{auction.id}", 0 , -1)
    newStore = Storage.objects.create(auctId = auction, auctJson=str(lista))
    newStore.save()
    #creating JSON file with the winner's info
    winDict = { 
        auction.id: { 
            'id': auction.id, 
            'object':auction.nobject, 
            'price':auction.price, 
            'publicDate': str(auction.publicData), 
            'endDate': str(auction.endData),
            'username':winn['username'], 
            'email':winn['email']
        }}

    winJson = json.dumps(winDict)
    auction.saveOnChain(winJson)

#Retrieve workflow of the auctions
def getWorkflow():
    wf = client.lrange("workflow", 0, -1)
    return wf





