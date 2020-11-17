
from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User
import redis
import json
from user.models import Auct
from .utils import *


client = redis.StrictRedis(host='127.0.0.1', port=6379, password='',db=0)

def addAuction(auctionId):  #The admin user add this auction on Redis
    dettAuct = Auct.objects.filter(id=auctionId).values()
    thisAuct = dettAuct[0]
    client.lpush(f"Auction{thisAuct['id']}", f"Starting price: {thisAuct['price']} euro")




def tip(identif, pricef, userf, date):
    client.rpush(f"Auction{identif}", f"{userf} has offered {pricef} | {date}")
    
    #update the work-flow list on Redis
    client.rpush("workflow", f"{userf} has offered {pricef} euro on Auction{identif}")





#The result is permanently saved on Sqlite and Ropsten(Json)
def permanentSaving(auction, winner): 
    winn = User.objects.filter(username=winner).values()[0]

    client.rpush("workflow", f"{winn['username']} has win the auction{auction.id}")


    #creating JSON file with the winner's info
    winJson = auction.id,[{ 'id': auction.id, 'object':auction.nobject, 'price':auction.price, 'publicDate': auction.publicData, 'endDate': auction.endData},{'username':winn['username'], 'email':winn['email']}]
    
    #Send the transaction to save the data on blockchain
    #sendTransaction(winJson)



def getWorkflow():
    wf = client.lrange("workflow", 0, -1)
    return wf

