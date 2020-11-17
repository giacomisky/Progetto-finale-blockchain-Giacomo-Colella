from django.contrib import admin
from .models import Auct, Feed

admin.site.register([Auct, Feed])
