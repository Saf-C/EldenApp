from django.shortcuts import render

# Create your views here.



# EldenRingInsider/views.py
from django.shortcuts import render
from .models import Item
from itertools import groupby
from operator import attrgetter


def item_list(request):
    items = Item.objects.all().order_by('item_type')

    for item in items:
        print(f"Item: {item.name}, Type: {item.item_type}, Description: {item.description}")

    grouped_items = {k: list(v) for k, v in groupby(items, attrgetter('item_type'))}

    # Debug: Print the structure of grouped_items
    for item_type, items_list in grouped_items.items():
        print(f"Item Type: {item_type}")
        for item in items_list:
            print(f"  - {item.name}: {item.description[:200]}...")  # Print first 200 chars of description

    return render(request, 'item_list.html', {'grouped_items': grouped_items})





