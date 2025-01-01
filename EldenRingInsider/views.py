from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, Django!")

# EldenRingInsider/views.py
from django.shortcuts import render
from .models import Item

def item_list(request):
    items = Item.objects.all()  # Get all items from the database
    print(items), # For debugging
    return render(request, 'item_list.html', {'items': items})
