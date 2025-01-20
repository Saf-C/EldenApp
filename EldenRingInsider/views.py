from django.shortcuts import render

# Create your views here.



# EldenRingInsider/views.py
from django.shortcuts import render
from .models import Item
from itertools import groupby

def item_list(request):
    # Get the search query from the request
    query = request.GET.get('q', '')

    # Fetch items based on the search query or all items if no query is provided
    if query:
        items = Item.objects.filter(name__icontains=query)
    else:
        items = Item.objects.all()

    # Group items by their type
    grouped_items = {}
    for item in items:
        if item.type not in grouped_items:
            grouped_items[item.type] = []
        grouped_items[item.type].append(item)

    # Pass the grouped items to the template
    return render(request, 'item_list.html', {'grouped_items': grouped_items, 'items' : items, 'query' : query})











