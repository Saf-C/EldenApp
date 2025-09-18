# myproject/EldenRingInsider/views.py
import json
import random
from collections import OrderedDict, defaultdict

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from .models import Item, Build, EquipmentSlot

# ------------------------------
# Small configuration / helpers
# ------------------------------
# map display attribute names
ATTRIBUTE_TO_EFFECT = {
    "Maximum Equip Load": "equip_load_boost",
    "Maximum Health": "health_boost",
    "Maximum Focus (FP)": "fp_boost",
    "Maximum Stamina": "stamina_boost",
    "Sorcery Potency": "spell_boost",
    "Incantation Potency": "incantation_boost",
    "Magic Attack Power": "magic_spell_boost",
    "Fire Attack Power": "fire_incantation_boost",
    "Lightning Attack Power": "lightning_incantation_boost",
    "Charged Spell Power": "charge_spell_boost",
    "Charged Incantation Power": "charge_incantation_boost",
    "Spell Duration": "spell_duration_boost",
    "Casting Speed": "casting_speed_boost",
    "Strength": "strength_boost",
    "Dexterity": "dexterity_boost",
    "Intelligence": "intelligence_boost",
    "Faith": "faith_boost",
    "Arcane": "arcane_boost",
    "Item Discovery": "item_discovery_boost",
    "Status Effect Buildup": "status_effect_boost",
    "Defense": "defense_boost",
}

# Weapon type universe used across endpoints
ALL_WEAPON_TYPES = [
    'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword', 'greatsword',
    'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
    'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'thrusting_sword', 'claw', 'fists',
    'backhand_blade', 'reaper', 'whip',
    'small_shield', 'medium_shield', 'greatshield',
    'staff', 'glintstone_staff', 'sacred_seal',
    'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
    'torch',
]

# Preferred weapon types by main stat
PREFERRED_WEAPON_TYPES = {
    'strength': ['greatsword', 'colossal_sword', 'colossal_weapon', 'great_axe', 'great_hammer', 'hammer', 'axe'],
    'dexterity': ['katana', 'great_katana', 'twinblade', 'curved_sword', 'straightsword', 'dagger'],
    'intelligence': ['staff', 'glintstone_staff'],
    'faith': ['sacred_seal', 'sacred_seal', 'staff'],  # seals / staves for faith-casting builds
    'arcane': ['katana', 'twinblade', 'dagger', 'twinblade'],
}

# Spell type preferences by main stat
PREFERRED_SPELL_TYPES = {
    'intelligence': ['spell'],   # we store in DB as type 'spell'
    'faith': ['incantation'],
}

# small utility: safe lowercase name/desc
def _text_of(item):
    name = getattr(item, 'name', '') or ''
    desc = getattr(item, 'description', '') or ''
    return f"{name} {desc}".lower()

def meets_required_stats(item, stats):
    """
    If item.required_stats exists and is a mapping, ensure the user's stats meet them.
    Accepts keys with flexible capitalization: 'Strength' or 'strength'
    If no required_stats present, returns True.
    """
    req = getattr(item, 'required_stats', None)
    if not req:
        return True
    # try both direct and lowercased keys
    for k, v in dict(req).items():
        if k is None:
            continue
        key = str(k).lower()
        user_val = stats.get(key, stats.get(k, 0))
        try:
            if int(user_val) < int(v):
                return False
        except Exception:
            # non-int values: be conservative and keep the item
            continue
    return True

def talisman_has_effect(talisman, effect_names):
    """
    Robust check for talisman.effects. Accepts:
     - None
     - string (we check substrings)
     - list of dicts with 'attribute' keys (older format)
    """
    eff = getattr(talisman, 'effects', None)
    if not eff:
        return False
    if isinstance(eff, str):
        txt = eff.lower()
        return any(name.lower() in txt for name in effect_names)
    if isinstance(eff, list):
        for e in eff:
            if isinstance(e, dict):
                attr = e.get('attribute') or e.get('name') or ''
                mapped = ATTRIBUTE_TO_EFFECT.get(attr, attr)
                if mapped and mapped in effect_names:
                    return True
    return False

# ------------------------------
# UI: Items / Builds / Pages
# ------------------------------
def item_list(request):
    query = request.GET.get('q', '')
    item_type = request.GET.get('type', '')
    item_type_order = [
        'katana', 'great_katana', 'colossal_sword', 'colossal_weapon', 'curved_sword', 'straightsword', 'greatsword',
        'dagger', 'twinblade', 'axe', 'great_axe', 'hammer', 'great_hammer', 'flail', 'spear',
        'short_spear', 'great_spear', 'halberd', 'heavy_thrusting_sword', 'thrusting_sword', 'claw', 'fists',
        'backhand_blade', 'reaper', 'whip',
        'small_shield', 'medium_shield', 'greatshield',
        'staff', 'glintstone_staff', 'sacred_seal',
        'ballista', 'crossbow', 'bow', 'light_bow', 'greatbow',
        'torch',
        'armor', 'spell', 'incantation', 'sorcery', 'talisman', 'ash_of_war', 'consumable', 'other',
    ]
    type_index = {t: i for i, t in enumerate(item_type_order)}

    items_qs = Item.objects.all()

    if query:
        items_qs = Item.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(type__icontains=query)
        )
    if item_type:
        item_types_list = item_type.split(',')
        items_qs = items_qs.filter(type__in=item_types_list)
    else:
        items_qs = Item.objects.all()

    items_list = list(items_qs)
    items_list.sort(key=lambda x: (type_index.get(x.type, len(item_type_order)), (x.name or "").lower()))

    paginator = Paginator(items_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    temp_grouped = defaultdict(list)
    for item in page_obj.object_list:
        temp_grouped[item.type].append(item)

    grouped_items = OrderedDict()
    for t in item_type_order:
        if t in temp_grouped:
            grouped_items[t] = temp_grouped[t]
    for t in temp_grouped:
        if t not in grouped_items:
            grouped_items[t] = temp_grouped[t]

    query_string = ''
    if query:
        query_string += f'q={query}&'
    if item_type:
        query_string += f'type={item_type}&'

    return render(request, 'item_list.html', {
        'grouped_items': grouped_items,
        'query': query,
        'page_obj': page_obj,
        'query_string': query_string
    })


# Helper function to format item scaling from JSON to a string
def format_scaling(scaling_data):
    if not scaling_data or not isinstance(scaling_data, dict):
        # This will return 'N/A' if the data is None, an empty dict, or not a dict.
        return 'N/A'

    # Define the scaling grade logic
    def get_grade(value):
        if value is None:
            return 'None'
        try:
            val = float(value)
            if val < 0.25:
                return 'E'
            elif 0.25 <= val < 0.6:
                return 'D'
            elif 0.6 <= val < 0.9:
                return 'C'
            elif 0.9 <= val < 1.4:
                return 'B'
            elif 1.4 <= val <= 1.75:
                return 'A'
            elif val > 1.75:
                return 'S'
            else:
                return 'N/A'
        except (ValueError, TypeError):
            # This is a key part for debugging.
            # If the value isn't a number, it will show the raw value and an error message.
            return f"Error: '{value}'"

    formatted_list = []
    # The keys in the scaling JSON are the stat names, and values are the numerical scaling ratios.
    for stat, value in scaling_data.items():
        grade = get_grade(value)
        formatted_list.append(f"{stat.capitalize()}: {grade}")

    return ', '.join(formatted_list)


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    formatted_scaling = format_scaling(item.scaling)
    return render(request, 'item_detail.html', {'item': item, 'formatted_scaling': formatted_scaling})


def builds_view(request):
    query = request.GET.get('q', '')
    builds = Build.objects.prefetch_related('equipment_slots__item').all()
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

    # ordering + pagination
    paginator = Paginator(builds, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'builds.html', {'builds': page_obj, 'page_obj': page_obj, 'slot_order': slot_order})


def build_page(request):
    # used by your build page (keeps compatibility)
    weapons = Item.objects.filter(type__in=ALL_WEAPON_TYPES)
    armors = Item.objects.filter(type='armor')
    talismans = Item.objects.filter(type='talisman')
    spells = Item.objects.filter(type='spell')
    ash_of_wars = Item.objects.filter(type='ash_of_war')

    session_build = request.session.get('custom_build', {})
    custom_build = {}
    for slot, item_id in session_build.items():
        try:
            custom_build[slot] = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            custom_build[slot] = None

    # show page (your template expects certain context)
    return render(request, 'builds.html', {
        'weapons': weapons,
        'armors': armors,
        'talismans': talismans,
        'spells': spells,
        'ash_of_wars': ash_of_wars,
        'custom_build': custom_build,
    })


# ------------------------------
# Stat-only recommendation endpoint
# ------------------------------

@require_POST
def recommend_build(request):
    """
    Expects JSON body with stat keys:
      { vigor, mind, endurance, strength, dexterity, intelligence, faith, arcane }
    Returns JSON with keys:
      weapons (list of dicts), head, body, arms, legs (each list of 1 dict or empty),
      spells (list), talismans (list length 4), ash_of_wars (list length 2)
    Each dict: { id, name, image_url }
    """
    try:
        body = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # normalize stat names to lowercase to be robust
    stats = {k.lower(): int(v) if isinstance(v, (int, float, str)) and str(v).isdigit() else v for k, v in body.items()}

    # Ensure required numeric defaults
    for k in ['vigor', 'mind', 'endurance', 'strength', 'dexterity', 'intelligence', 'faith', 'arcane']:
        stats.setdefault(k, 10)

    # choose main stat
    stat_candidates = {
        'strength': int(stats.get('strength', 0)),
        'dexterity': int(stats.get('dexterity', 0)),
        'intelligence': int(stats.get('intelligence', 0)),
        'faith': int(stats.get('faith', 0)),
        'arcane': int(stats.get('arcane', 0)),
    }
    main_stat = max(stat_candidates.items(), key=lambda x: x[1])[0]

    # ---------------------
    # helper: score and pick
    # ---------------------
    def pick_items(queryset, stats_local, prefer_types=None, prefer_name_tokens=None, limit=5):
        """
        Convert queryset into a scored list of items (simple heuristics), return top `limit` items (as list of model instances)
        """
        candidates = []
        prefer_types = set(prefer_types or [])
        prefer_name_tokens = [t.lower() for t in (prefer_name_tokens or [])]

        for item in queryset:
            # skip if user doesn't meet required stats
            if not meets_required_stats(item, stats_local):
                continue

            score = 0
            name_desc = _text_of(item)

            # boost for preferred type
            if item.type in prefer_types:
                score += 3

            # boost when main_stat appears in name/desc or preferred tokens
            if main_stat in name_desc:
                score += 2
            for tok in prefer_name_tokens:
                if tok in name_desc:
                    score += 1

            # small random tie-break
            score += random.random() * 0.01

            candidates.append((score, item))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return [c[1] for c in candidates[:limit]]

    # ---------------------
    # Weapons
    # ---------------------
    # gather a pool of weapon types we want to search across
    weapon_pool_types = ALL_WEAPON_TYPES
    all_weapons_qs = Item.objects.filter(type__in=weapon_pool_types)

    preferred_types = PREFERRED_WEAPON_TYPES.get(main_stat, [])
    # prefer exact weapon names if the stat implies (e.g., Rivers of Blood for bleed/dex)
    prefer_tokens = []
    if main_stat == 'dexterity':
        prefer_tokens = ['katana', 'uchigatana', 'nagakiba', 'rivers of blood']
    elif main_stat == 'strength':
        prefer_tokens = ['greatsword', 'claymore', 'giant', 'crusher']
    elif main_stat == 'intelligence':
        prefer_tokens = ['staff', 'moonveil', 'dark moon', 'sorcery']
    elif main_stat == 'faith':
        prefer_tokens = ['seal', 'incantation', 'golden vow']
    elif main_stat == 'arcane':
        prefer_tokens = ['bleed', 'lord of blood', 'eleonora', 'occult']

    chosen_weapons = pick_items(all_weapons_qs, stats, prefer_types=preferred_types, prefer_name_tokens=prefer_tokens, limit=8)

    # ensure we provide 4 weapon slots (RH1, RH2, LH1, LH2) for the front-end
    # if not enough weapons, duplicate sensible choices
    weapons_result = []
    used_names = set()
    i = 0
    while len(weapons_result) < 4 and i < len(chosen_weapons):
        item = chosen_weapons[i]
        if item.name not in used_names:
            weapons_result.append(item)
            used_names.add(item.name)
        i += 1
    # fallback: pad with any weapons from DB that meet requirements
    if len(weapons_result) < 4:
        for item in all_weapons_qs:
            if item.name not in used_names and meets_required_stats(item, stats):
                weapons_result.append(item)
                used_names.add(item.name)
            if len(weapons_result) >= 4:
                break
    # final pad with None
    while len(weapons_result) < 4:
        weapons_result.append(None)

    # ---------------------
    # Armor (head/body/arms/legs)
    # ---------------------
    all_armors_qs = Item.objects.filter(type__in=['head', 'body', 'arms', 'legs'])
    # Simple scoring per-piece
    def pick_best_armor_piece(slot_type):
        candidates = [a for a in all_armors_qs if a.type == slot_type and meets_required_stats(a, stats)]
        if not candidates:
            return None
        # prefer heavy armor for high endurance, magic for intelligence/mind, poise for str/dex
        def armor_score(a):
            s = 0
            name_desc = _text_of(a)
            endurance = stats.get('endurance', 10)
            intelligence = stats.get('intelligence', 10)
            dex = stats.get('dexterity', 10)
            if endurance >= 30:
                s += (getattr(a, 'weight', 0) or 0) * 1.5
            if intelligence >= 30 and 'magic' in name_desc:
                s += 5
            if dex >= 30 and ('light' in name_desc or 'knife' in name_desc):
                s += 3
            s += random.random() * 0.01
            return s
        return max(candidates, key=armor_score)

    head = pick_best_armor_piece('head')
    body = pick_best_armor_piece('body')
    arms = pick_best_armor_piece('arms')
    legs = pick_best_armor_piece('legs')

    # ---------------------
    # Spells (4)
    # ---------------------
    all_spells_qs = Item.objects.filter(type__in=['spell', 'incantation'])
    spell_prefer = PREFERRED_SPELL_TYPES.get(main_stat, None)
    chosen_spells = pick_items(all_spells_qs, stats, prefer_types=spell_prefer or [], prefer_name_tokens=[], limit=8)
    spells_result = chosen_spells[:4]
    # pad
    while len(spells_result) < 4:
        spells_result.append(None)

    # ---------------------
    # Talismans (4) - try to use effects when present
    # ---------------------
    all_talismans_qs = Item.objects.filter(type='talisman')
    talisman_candidates = []
    for t in all_talismans_qs:
        if not meets_required_stats(t, stats):
            continue
        score = 0
        name_desc = _text_of(t)
        # use talisman_has_effect when possible
        if main_stat == 'intelligence' and talisman_has_effect(t, ['spell_boost', 'magic_spell_boost', 'intelligence_boost', 'spell_duration_boost']):
            score += 4
        if main_stat == 'faith' and talisman_has_effect(t, ['incantation_boost', 'faith_boost', 'fp_boost']):
            score += 4
        if main_stat == 'strength' and talisman_has_effect(t, ['strength_boost', 'equip_load_boost']):
            score += 3
        if main_stat == 'dexterity' and talisman_has_effect(t, ['dexterity_boost', 'casting_speed_boost']):
            score += 3
        if main_stat == 'arcane' and talisman_has_effect(t, ['arcane_boost', 'status_effect_boost']):
            score += 3

        # fallback name hints
        if main_stat in name_desc:
            score += 1
        # small tie-breaker
        score += random.random() * 0.01
        talisman_candidates.append((score, t))
    talisman_candidates.sort(key=lambda x: x[0], reverse=True)
    talismans_result = [t for _, t in talisman_candidates[:4]]
    # pad
    while len(talismans_result) < 4:
        talismans_result.append(None)

    # ---------------------
    # Ashes of War (2)
    # ---------------------
    all_ashes_qs = Item.objects.filter(type='ash_of_war')
    # choose based on simple token match and requirements
    ash_tokens = {
        'strength': ['lion', 'giant', 'cragblade', 'crusher', 'hammer'],
        'dexterity': ['unsheathe', 'double', 'quickstep', 'double slash', 'piercing'],
        'intelligence': ['magic', 'carian', 'glintstone', 'sorcery'],
        'faith': ['golden', 'blessing', 'sacred', 'faith'],
        'arcane': ['seppuku', 'blood', 'bloodflame', 'bleed'],
    }
    prefer_ashes_tokens = ash_tokens.get(main_stat, [])
    chosen_ashes = []
    for ash in all_ashes_qs:
        if not meets_required_stats(ash, stats):
            continue
        name_desc = _text_of(ash)
        score = 0
        for tok in prefer_ashes_tokens:
            if tok in name_desc:
                score += 2
        score += random.random() * 0.01
        chosen_ashes.append((score, ash))
    chosen_ashes.sort(key=lambda x: x[0], reverse=True)
    ashes_result = [a for _, a in chosen_ashes[:2]]
    while len(ashes_result) < 2:
        ashes_result.append(None)

    # ---------------------
    # Build JSON payload (convert items to small dicts)
    # ---------------------
    def item_to_small_dict(item):
        if not item:
            return None
        return {'id': getattr(item, 'id', None), 'name': getattr(item, 'name', None), 'image_url': getattr(item, 'image_url', None)}

    response_payload = {
        'weapons': [item_to_small_dict(i) for i in weapons_result],  # RH1, RH2, LH1, LH2
        'head': [item_to_small_dict(head)] if head else [],
        'body': [item_to_small_dict(body)] if body else [],
        'arms': [item_to_small_dict(arms)] if arms else [],
        'legs': [item_to_small_dict(legs)] if legs else [],
        'spells': [item_to_small_dict(s) for s in spells_result],
        'talismans': [item_to_small_dict(t) for t in talismans_result],
        'ash_of_wars': [item_to_small_dict(a) for a in ashes_result],
        'main_stat': main_stat,
    }

    return JsonResponse(response_payload)


# ------------------------------
# Utility endpoints used by front-end
# ------------------------------
def get_or_create_custom_build(user):
    return {
        'RH1': None,
        'RH2': None,
        'LH1': None,
        'LH2': None,
        'Helms': None,
        'Chest Armor': None,
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
        'AshOfWar1': None,
        'AshOfWar2': None,
    }


@require_GET
def get_items(request):
    item_type = request.GET.get('type')
    if item_type in ['head', 'body', 'arms', 'legs', 'talisman', 'spell', 'ash_of_war']:
        items = Item.objects.filter(type=item_type).values('id', 'name', 'image_url')
    elif item_type == 'weapon':
        items = Item.objects.filter(type__in=ALL_WEAPON_TYPES).values('id', 'name', 'image_url')
    else:
        items = Item.objects.none()
    return JsonResponse(list(items), safe=False)



@require_POST
def save_item_to_build(request):
    data = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
    slot = data.get('slot')
    item_id = data.get('item_id')

    build = request.session.get('custom_build', {})
    build[slot] = item_id
    request.session['custom_build'] = build

    return JsonResponse({'status': 'success'})


@require_POST
def save_as_preset(request):
    data = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
    name = data.get('name')
    description = data.get('description', '')
    custom_build = request.session.get('custom_build', {})
    build = Build.objects.create(name=name, description=description)
    for slot_name, item_id in custom_build.items():
        if item_id:
            EquipmentSlot.objects.create(build=build, slot_name=slot_name, item_id=item_id)
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
        'icon': getattr(item, 'icon', None),
    })

def credits_view(request):
    return render(request, 'credits.html')

def about_view(request):
    return render(request, 'about.html')

