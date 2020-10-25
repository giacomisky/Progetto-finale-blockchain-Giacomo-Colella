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