from django.db import models
from django.contrib.auth.models import User
import hashlib
from managing.utils import sendTransaction


class Auct(models.Model):
    nobject = models.CharField(max_length=18)
    price = models.FloatField(default=0)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    publicData = models.DateTimeField(auto_now_add=True)
    endData = models.DateTimeField()
    active = models.BooleanField(default=True)
    hashAuct = models.CharField(max_length=32, default=None, null=True, blank=True)
    txId = models.CharField(max_length=66, default=None, null=True, blank=True)

    def saveOnChain(self, jsonData):
        self.hashAuct = hashlib.sha256(jsonData.encode('utf-8')).hexdigest()
        self.txId = sendTransaction(self.hashAuct)
        self.save()

class Feed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Storage(models.Model):
    auctId = models.ForeignKey(Auct, on_delete=models.CASCADE)
    auctJson = models.TextField()

    def __str__(self):
        return self.auctJson

    
class Wallet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    privateKey = models.TextField()
    ethBalance = models.FloatField(default=0)
    euroBalance = models.FloatField(default=0)
    


