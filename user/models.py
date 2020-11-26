from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class Auct(models.Model):
    nobject = models.CharField(max_length=18) #name of object
    price = models.FloatField(default=0)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    publicData = models.DateTimeField(auto_now_add=True)
    endData = models.DateTimeField()
    active = models.BooleanField(default=True)

    def getBuyer(self):
        return self.buyer

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