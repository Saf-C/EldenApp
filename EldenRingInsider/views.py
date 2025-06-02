from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from collections import OrderedDict, defaultdict

from unicodedata import category

from .models import Item, Build
from django.db.models import Q


def item_list(request):
    query = request.GET.get('q', '')
    # Use database values for ordering
    item_type_order = [
        'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword',
        'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
        'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'claw', 'fists',
        'backhand_blade', 'reaper', 'whip',
        'small_shield', 'medium_shield', 'greatshield',
        'staff', 'glintstone_staff', 'sacred_seal',
        'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
        'torch',
        'armor', 'spell', 'incantation', 'sorcery', 'talisman', 'ash_of_war', 'consumable', 'other',
    ]

    type_index = {t: i for i, t in enumerate(item_type_order)}

    # Filter queryset if query present
    if query:
        items_qs = Item.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(type__icontains=query)
        )
    else:
        items_qs = Item.objects.all()

    # Evaluate queryset to list for Python sorting
    items_list = list(items_qs)

    # Sort by custom type order, then by name
    items_list.sort(key=lambda x: (type_index.get(x.type, len(item_type_order)), x.name.lower()))

    # Paginate the sorted list
    paginator = Paginator(items_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Group items on current page by type
    temp_grouped = defaultdict(list)
    for item in page_obj.object_list:
        temp_grouped[item.type].append(item)

    # Order groups according to item_type_order, append any others at the end
    grouped_items = OrderedDict()
    for t in item_type_order:
        if t in temp_grouped:
            grouped_items[t] = temp_grouped[t]
    for t in temp_grouped:
        if t not in grouped_items:
            grouped_items[t] = temp_grouped[t]

    return render(request, 'item_list.html', {
        'grouped_items': grouped_items,
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
        'icon': item.icon,
    })
