from django.shortcuts import render

# Create your views here.



# EldenRingInsider/views.py
from django.shortcuts import render
from .models import Item
from django.db.models import Q  # Import Q for complex queries
from itertools import groupby
from django.shortcuts import render, get_object_or_404


def item_list(request):

    # Get the search query from the request
    query = request.GET.get('q', '')

    # Filter items based on the query or get all items if no query is provided
    if query:
        items = Item.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(type__icontains=query)
        )
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


def item_detail(request, item_id):
    # Get the specific item or return a 404 if not found
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'item_detail.html', {'item': item})








