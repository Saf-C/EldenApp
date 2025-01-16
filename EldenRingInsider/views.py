from django.shortcuts import render

# Create your views here.



# EldenRingInsider/views.py
from django.shortcuts import render
from .models import Item
from itertools import groupby

def item_list(request):
    # Fetch all items from the database
    items = Item.objects.all()

    # Group items by their type
    grouped_items = {}
    for item in items:
        if item.type not in grouped_items:
            grouped_items[item.type] = []
        grouped_items[item.type].append(item)

    # Pass the grouped items to the template
    return render(request, 'item_list.html', {'grouped_items': grouped_items})











