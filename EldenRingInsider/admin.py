from django.contrib import admin

# Register your models here.
# EldenRingInsider/admin.py
from django.contrib import admin
from .models import Item

# Register the Item model with the admin interface
admin.site.register(Item)
