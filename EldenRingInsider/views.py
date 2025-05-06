

# Create your views here.



# EldenRingInsider/views.py
from .models import Item, ItemType
from django.db.models import Q  # Import Q for complex queries
from itertools import groupby
from django.shortcuts import render, get_object_or_404
from .models import Build
from django.http import JsonResponse
from django.core.paginator import Paginator
from collections import OrderedDict, defaultdict

def item_list(request):

    # Get the search query from the request
    query = request.GET.get('q', '')

    # Filter based on query or get all items
    if query:
        items = Item.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(type__icontains=query)
        )
    else:
        items = Item.objects.all().order_by('type', 'name')


    ITEM_TYPE_ORDER = [
        'Armor',
        'Weapon',
        'Spell',
        'Talisman',
        'Ash of War',
        'Consumable',
        'Other',
    ]

    # Grouping of items
    temp_grouped = defaultdict(list)
    for item in items:
        temp_grouped[item.get_type_display()].append(item)

    # Order them according to my list
    grouped_items = OrderedDict()
    for t in ITEM_TYPE_ORDER:
        if t in temp_grouped:
            grouped_items[t] = temp_grouped[t]

    # Anything that is not in the item type categories
    for t in temp_grouped:
        if t not in grouped_items:
            grouped_items[t] = temp_grouped[t]



    return render(request, 'item_list.html', {
        'grouped_items': dict(grouped_items),
        'query': query,
    })



def item_detail(request, item_id):
    # Get the specific item or return a 404 if not found
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'item_detail.html', {'item': item})


def builds_view(request):
    query = request.GET.get('q', '')
    builds = Build.objects.prefetch_related('equipment_slots__item')

    if query:
        builds = builds.filter(name__icontains=query)

    return render(request, 'builds.html', {'builds': builds, 'query': query})




def item_json_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return JsonResponse({
        'name': item.name,
        'description': item.description,
        'image_url': item.image_url,
    })









