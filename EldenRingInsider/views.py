from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from collections import OrderedDict, defaultdict
from .models import Item, Build
from django.db.models import Q

def item_list(request):
    query = request.GET.get('q', '')
    item_type_order = [
        'Armor',
        'Weapon',
        'Spell',
        'Talisman',
        'Ash of War',
        'Consumable',
        'Other',
    ]

    if query:
        items = Item.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(type__icontains=query)
        ).order_by('type', 'name')
    else:
        items = Item.objects.all().order_by('type', 'name')

    paginator = Paginator(items, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Group only the items on the current page
    temp_grouped = defaultdict(list)
    for item in page_obj.object_list:
        temp_grouped[item.get_type_display()].append(item)

    grouped_items = OrderedDict()
    for t in item_type_order:
        if t in temp_grouped:
            grouped_items[t] = temp_grouped[t]
    for t in temp_grouped:
        if t not in grouped_items:
            grouped_items[t] = temp_grouped[t]

    return render(request, 'item_list.html', {
        'grouped_items': dict(grouped_items),
        'query': query,
        'page_obj': page_obj,
    })

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'item_detail.html', {'item': item})

def builds_view(request):
    query = request.GET.get('q', '')
    builds = Build.objects.prefetch_related('equipment_slots__item')
    if query:
        builds = builds.filter(name__icontains=query)
    slot_order = [
        ('RH1', 'Right Hand 1'), ('RH2', 'Right Hand 2'),
        ('LH1', 'Left Hand 1'), ('LH2', 'Left Hand 2'),
        ('Helms', 'Helm'), ('Chest Armor', 'Chest'), ('Gauntlets', 'Gauntlets'), ('Greaves', 'Greaves'),
        ('Talisman1', 'Talisman 1'), ('Talisman2', 'Talisman 2'),
        ('Talisman3', 'Talisman 3'), ('Talisman4', 'Talisman 4'),
        ('Spell1', 'Spell 1'), ('Spell2', 'Spell 2'),
        ('Spell3', 'Spell 3'), ('Spell4', 'Spell 4'),
        ('AshOfWar1', 'Ash of War 1'), ('AshOfWar2', 'Ash of War 2'),
    ]
    return render(request, 'builds.html', {'builds': builds, 'query': query, 'slot_order': slot_order})


def item_json_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return JsonResponse({
        'name': item.name,
        'description': item.description,
        'image_url': item.image_url,
    })
