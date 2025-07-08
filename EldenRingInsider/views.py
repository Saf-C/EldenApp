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
    # Determine build type based on highest stat
    main_stat = max(stats, key=stats.get)
    is_mage = main_stat == 'intelligence'
    is_faith = main_stat == 'faith'
    is_strength = main_stat == 'strength'
    is_dexterity = main_stat == 'dexterity'

    # Helper function to filter and sort items
    def filter_and_sort(items, stat_key=None, preferred_types=None):
        # Filter for required stats
        filtered = []
        for item in items:
            req = item.required_stats or {}
            if all(stats.get(k, 99) >= v for k, v in req.items()):
                filtered.append(item)
        # Filter for preferred types if provided
        if preferred_types:
            filtered = [item for item in filtered if item.type in preferred_types]
        # Sort by scaling with main stat if provided
        if stat_key and all(hasattr(i, 'scaling') for i in filtered):
            filtered.sort(key=lambda x: x.scaling.get(stat_key, 0), reverse=True)
        return filtered[:5]

    # --- WEAPONS ---
    all_weapons = Item.objects.filter(
        type__in=[
            'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword',
            'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
            'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'claw', 'fists',
            'backhand_blade', 'reaper', 'whip',
            'small_shield', 'medium_shield', 'greatshield',
            'staff', 'glintstone_staff', 'sacred_seal',
            'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
            'torch',
        ]
    )
    if is_mage:
        weapons = filter_and_sort(all_weapons, 'intelligence', ['staff', 'glintstone_staff'])
    elif is_faith:
        weapons = filter_and_sort(all_weapons, 'faith', ['sacred_seal'])
    elif is_strength:
        weapons = filter_and_sort(all_weapons, 'strength', ['greatsword', 'colossal_sword', 'colossal_weapon', 'great_axe', 'great_hammer'])
    elif is_dexterity:
        weapons = filter_and_sort(all_weapons, 'dexterity', ['katana', 'great_katana', 'twinblade', 'dagger', 'curved_sword'])
    else:
        weapons = filter_and_sort(all_weapons)

    # --- ARMOR ---
    all_armors = Item.objects.filter(type__in=['head', 'body', 'arms', 'legs'])
    selected_armors = pick_armor_by_stats(all_armors, stats)

    head = selected_armors['head']
    body = selected_armors['body']
    arms = selected_armors['arms']
    legs = selected_armors['legs']



    # --- SPELLS ---
    all_spells = Item.objects.filter(type__in=['spell', 'incantation'])
    if is_mage:
        spells = filter_and_sort(all_spells, 'intelligence', ['spell'])
    elif is_faith:
        spells = filter_and_sort(all_spells, 'faith', ['incantation'])
    else:
        spells = filter_and_sort(all_spells)

    # --- TALISMANS ---
    all_talismans = Item.objects.filter(type='talisman')

    for t in all_talismans:
        print(t.name, t.effects)

    is_mage = ...  # True if Intelligence build
    is_faith = ...  # True if Faith build
    is_strength = ...  # True if Strength build
    is_dexterity = ...  # True if Dexterity build
    is_arcane = ...  # True if Arcane build
    is_tank = ... #True if Vigor Build

    if is_mage:
        # Intelligence-focused: sorceries and FP
        talismans = [t for t in all_talismans if t.effects in [
            'spell_boost', 'magic_spell_boost', 'charge_spell_boost', 'spell_duration_boost',
            'fp_boost', 'intelligence_boost'
        ]]
    elif is_faith:
        # Faith-focused: incantations and FP
        talismans = [t for t in all_talismans if t.effects in [
            'incantation_boost', 'fire_incantation_boost', 'lightning_incantation_boost',
            'charge_incantation_boost', 'spell_duration_boost', 'faith_boost', 'fp_boost'
        ]]
    elif is_strength:
        # Strength-focused: melee and survivability
        talismans = [t for t in all_talismans if t.effects in [
            'strength_boost', 'health_boost', 'stamina_boost', 'equip_load_boost'
        ]]
    elif is_dexterity:
        # Dexterity-focused: speed and survivability
        talismans = [t for t in all_talismans if t.effects in [
            'dexterity_boost', 'health_boost', 'stamina_boost', 'equip_load_boost', 'casting_speed_boost'
        ]]
    elif is_arcane:
        # Arcane-focused: item discovery and status
        talismans = [t for t in all_talismans if t.effects in [
            'arcane_boost', 'item_discovery_boost', 'status_effect_boost'
        ]]
    elif is_tank:
        # Tank/general: health, stamina, equip load, defense
        talismans = [t for t in all_talismans if t.effects in [
            'health_boost', 'stamina_boost', 'equip_load_boost', 'defense_boost'
        ]]
    else:
        # Fallback: all talismans
        talismans = all_talismans

    # Further filter by required stats, then limit to top 4
    talismans = [t for t in talismans if all(stats.get(k, 99) >= v for k, v in (t.required_stats or {}).items())][:4]

    # --- ASHES OF WAR ---
    all_ashes = Item.objects.filter(type='ash_of_war')
    # (No stat-based filtering for ashes)
    ashes = filter_and_sort(all_ashes)



    return JsonResponse({
        'weapons': [{'id': w.id, 'name': w.name, 'image_url': w.image_url} for w in weapons],
        'head': [{'id': head.id, 'name': head.name, 'image_url': head.image_url}] if head else [],
        'body': [{'id': body.id, 'name': body.name, 'image_url': body.image_url}] if body else [],
        'arms': [{'id': arms.id, 'name': arms.name, 'image_url': arms.image_url}] if arms else [],
        'legs': [{'id': legs.id, 'name': legs.name, 'image_url': legs.image_url}] if legs else [],
        'spells': [{'id': s.id, 'name': s.name, 'image_url': s.image_url} for s in spells],
        'talismans': [{'id': t.id, 'name': t.name, 'image_url': t.image_url} for t in talismans],
        'ash_of_wars': [{'id': ash.id, 'name': ash.name, 'image_url': ash.image_url} for ash in ashes],
    })

def pick_armor_by_stats(armors, stats):
    """
    Selects the best armor for each slot based on build stats.
    Returns a dict: {'head': best_head, 'body': best_body, 'arms': best_arms, 'legs': best_legs}
    """
    # Determine main stat(s)
    main_stat = max(stats, key=stats.get)
    endurance = stats.get('endurance', 10)
    intelligence = stats.get('intelligence', 10)
    mind = stats.get('mind', 10)
    strength = stats.get('strength', 10)
    dexterity = stats.get('dexterity', 10)

    # Define scoring for each armor piece
    def score(armor):
        s = 0
        # Endurance: prefer heavier armor
        if endurance >= 30:
            s += (armor.weight or 0) * 2
        elif endurance >= 20:
            s += (armor.weight or 0) * 1.2
        else:
            s += max(0, 20 - (armor.weight or 0))  # prefer lighter if low endurance

        # Intelligence/Mind: prefer magic defense/effects
        if intelligence >= 30 or mind >= 30:
            if armor.effects and 'magic' in armor.effects.lower():
                s += 15
            s += (armor.defense.get('magic', 0) if armor.defense else 0)

        # Strength/Dexterity: prefer physical defense/poise
        if strength >= 30 or dexterity >= 30:
            if armor.effects and ('poise' in armor.effects.lower() or 'physical' in armor.effects.lower()):
                s += 15
            s += (armor.defense.get('physical', 0) if armor.defense else 0)
            # If you have a poise stat, add it here as well

        return s

    # For each slot, pick the best armor by score
    selected = {}
    for slot in ['head', 'body', 'arms', 'legs']:
        candidates = [a for a in armors if a.type == slot]
        if candidates:
            best = max(candidates, key=score)
            selected[slot] = best
        else:
            selected[slot] = None
    return selected


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
    if item_type in ['head', 'body', 'arms', 'legs', 'talisman', 'spell', 'ash_of_war']:
        items = Item.objects.filter(type=item_type).values('id', 'name', 'image_url')
    elif item_type == 'weapon':
        weapon_types = [ 'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword',
        'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
        'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'claw', 'fists',
        'backhand_blade', 'reaper', 'whip',
        'small_shield', 'medium_shield', 'greatshield',
        'staff', 'glintstone_staff', 'sacred_seal',
        'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
        'torch',]
        items = Item.objects.filter(type__in=weapon_types).values('id', 'name', 'image_url')
    else:
        items = Item.objects.none()
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
