from django.shortcuts import render, get_object_or_404

from django.core.paginator import Paginator
from collections import OrderedDict, defaultdict

from unicodedata import category

from .models import Item, Build, EquipmentSlot
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import json



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


def build_page(request):
    # Retrieve all relevant items for each slot type
    weapons = Item.objects.filter(type__in=[ 'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword',
        'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
        'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'claw', 'fists',
        'backhand_blade', 'reaper', 'whip',
        'small_shield', 'medium_shield', 'greatshield',
        'staff', 'glintstone_staff', 'sacred_seal',
        'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
        'torch',])
    armors = Item.objects.filter(type='armor')
    talismans = Item.objects.filter(type='talisman')
    spells = Item.objects.filter(type='spell')
    ash_of_wars = Item.objects.filter(type='ash_of_war')

    # Get session build data
    session_build = request.session.get('custom_build', {})

    # Create context with actual item objects
    custom_build = {}
    for slot, item_id in session_build.items():
        try:
            custom_build[slot] = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            custom_build[slot] = None


    # Retrieve or initialize the user's custom build (session or user profile)
    #custom_build = get_or_create_custom_build(request.user)


@require_POST
def recommend_build(request):
    stats = json.loads(request.body)
    # weapons
    all_weapons = Item.objects.filter(
        type__in=[ 'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword',
                'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
                'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'claw', 'fists',
                'backhand_blade', 'reaper', 'whip',
                'small_shield', 'medium_shield', 'greatshield',
                'staff', 'glintstone_staff', 'sacred_seal',
                'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
                'torch',]
    )
    weapons = []
    for item in all_weapons:
        req = item.required_stats or {}
        # Only include items where all required stats are met
        if all(stats.get(k, 99) >= v for k, v in req.items()):
            weapons.append(item)
    weapons = weapons[:5]

    # armors
    all_armors = Item.objects.filter(type='armor')
    armors = []
    for item in all_armors:
        req = item.required_stats or {}
        if all(stats.get(k, 99) >= v for k, v in req.items()):
            armors.append(item)
    armors = armors[:5]

    # talismans
    all_talismans = Item.objects.filter(type='talisman')
    talismans = []
    for item in all_talismans:
        req = item.required_stats or {}
        if all(stats.get(k, 99) >= v for k, v in req.items()):
            talismans.append(item)
    talismans = talismans[:5]

    # spells
    all_spells = Item.objects.filter(type__in=['spell', 'incantation'])
    spells = []
    for item in all_spells:
        req = item.required_stats or {}
        if all(stats.get(k, 99) >= v for k, v in req.items()):
            spells.append(item)
    spells = spells[:5]

    # ash_of_wars
    all_ash_of_wars = Item.objects.filter(type='ash_of_wars')
    ash_of_wars = []
    for item in all_ash_of_wars:
        req = item.required_stats or {}
        if all(stats.get(k, 99) >= v for k, v in req.items()):
            ash_of_wars.append(item)
    ash_of_wars = ash_of_wars[:5]

    return JsonResponse({
        'weapons': [{'id': w.id, 'name': w.name, 'image_url': w.image_url} for w in weapons],
        'armors': [{'id': a.id, 'name': a.name, 'image_url': a.image_url} for a in armors],
        'talismans': [{'id': a.id, 'name': a.name, 'image_url': a.image_url} for a in talismans],
        'spells': [{'id': s.id, 'name': s.name, 'image_url': s.image_url} for s in spells],
        'ash_of_wars': [{'id': s.id, 'name': s.name, 'image_url': s.image_url} for s in ash_of_wars],
    })


def get_or_create_custom_build(user):
    # If user is authenticated, you could use user.custom_build
    # For demo, just return a dict with empty slots
    return {
        'RH1': None,
        'RH2': None,
        'LH1': None,
        'LH2': None,
        'Helm': None,
        'Chest': None,
        'Gauntlets': None,
        'Greaves': None,
        'Talisman1': None,
        'Talisman2': None,
        'Talisman3': None,
        'Talisman4': None,
        'Spell1': None,
        'Spell2': None,
        'Spell3': None,
        'Spell4': None,
        'Ash_of_War1': None,
        'Ash_of_War2': None,
    }

@require_GET
def get_items(request):
    item_type = request.GET.get('type')
    # Map slot type to item types in your DB
    type_map = {
        'weapon': [ 'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword',
        'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
        'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'claw', 'fists',
        'backhand_blade', 'reaper', 'whip',
        'small_shield', 'medium_shield', 'greatshield',
        'staff', 'glintstone_staff', 'sacred_seal',
        'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
        'torch',],
        'armor': ['armor'],
        'talisman': ['talisman'],
        'spell': ['spell'],
        'ash_of_war': ['ash_of_war'],
    }
    types = type_map.get(item_type, [])
    items = Item.objects.filter(type__in=types).values('id', 'name', 'image_url')
    return JsonResponse(list(items), safe=False)



@csrf_exempt  # Only for development; use proper CSRF in production!
@require_POST
def save_item_to_build(request):
    data = json.loads(request.body)
    slot = data.get('slot')
    item_id = data.get('item_id')

    build = request.session.get('custom_build', {})
    build[slot] = item_id
    request.session['custom_build'] = build

    return JsonResponse({'status': 'success'})

@require_POST
def save_as_preset(request):
    data = json.loads(request.body)
    name = data.get('name')
    description = data.get('description', '')
    custom_build = request.session.get('custom_build', {})
    # Create a new Build object and EquipmentSlot objects for each slot
    return JsonResponse({'status': 'success'})

@require_POST
def clear_custom_build(request):
    request.session['custom_build'] = {}
    return JsonResponse({'status': 'success'})



def item_json_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return JsonResponse({
        'name': item.name,
        'description': item.description,
        'image_url': item.image_url,
        'icon': item.icon,
    })
