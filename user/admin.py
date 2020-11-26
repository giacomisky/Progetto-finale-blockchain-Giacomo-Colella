from django.contrib import admin
from .models import Auct, Feed, Storage

admin.site.register([Auct, Feed, Storage])
