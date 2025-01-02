from django.shortcuts import render

# Create your views here.



# EldenRingInsider/views.py
from django.shortcuts import render
from .models import Item

def item_list(request):
    # Fetch all items from the database
    items = Item.objects.all()

    # Pass all items to the template
    return render(request, 'item_list.html', {'items': items})



