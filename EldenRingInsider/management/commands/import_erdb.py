# EldenRingInsider/management/commands/import_erdb.py

import json
import os
from django.core.management.base import BaseCommand
from EldenRingInsider.models import Item, ItemType

# Map ERDB categories to your ItemType choices
ERDB_TO_ITEMTYPE = {
    # Armor
    "Head": ItemType.HEAD,
    "Body": ItemType.BODY,
    "Arms": ItemType.ARMS,
    "Legs": ItemType.LEGS,

    # Shields
    "Small Shield": ItemType.SMALL_SHIELD,
    "Medium Shield": ItemType.MEDIUM_SHIELD,
    "Greatshield": ItemType.GREATSHIELD,

    # Ranged
    "Ballista": ItemType.BALLISTA,
    "Bow": ItemType.BOW,
    "Light Bow": ItemType.LIGHT_BOW,
    "Crossbow": ItemType.CROSSBOW,
    "Greatbow": ItemType.GREATBOW,

    # Weapon
    "Claw": ItemType.CLAW,
    "Colossal Sword": ItemType.COLOSSAL_SWORD,
    "Colossal Weapon": ItemType.COLOSSAL_WEAPON,
    "Curved Greatsword": ItemType.CURVED_SWORD,
    "Curved Sword": ItemType.CURVED_SWORD,
    "Dagger": ItemType.DAGGER,
    "Flail": ItemType.FLAIL,
    "Glintstone Staff": ItemType.GLINTSTONE_STAFF,
    "Great Club": ItemType.GREAT_HAMMER,
    "Great Hammer": ItemType.GREAT_HAMMER,
    "Greatsword": ItemType.GREATSWORD,
    "Greataxe": ItemType.GREAT_AXE,
    "Halberd": ItemType.HALBERD,
    "Hammer": ItemType.HAMMER,
    "Heavy Thrusting Sword": ItemType.HEAVY_THRUSTING_SWORD,
    "Katana": ItemType.KATANA,
    "Reaper": ItemType.REAPER,
    "Spear": ItemType.SPEAR,
    "Straight Sword": ItemType.STRAIGHTSWORD,
    "Thrusting Sword": ItemType.THRUSTING_SWORD,
    "Torch": ItemType.TORCH,
    "Twinblade": ItemType.TWINBLADE,
    "Whip": ItemType.WHIP,
    "Axe": ItemType.AXE,
    "Great Spear": ItemType.GREAT_SPEAR,
    "Fist": ItemType.FISTS,

    # Spells
    "Sacred Seal": ItemType.SACRED_SEAL,
    "Sorcery": ItemType.SPELL,
    "Incantation": ItemType.SPELL,

    # Ashes of War
    "Ash Of War": ItemType.ASH_OF_WAR,
    "Consumable": ItemType.CONSUMABLE,

    # Talisman
    "Talisman": ItemType.TALISMAN,

}

class Command(BaseCommand):
    help = 'Import Elden Ring items from ERDB-generated JSON files, preserving manual images/locations.'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join("data", "1.10.0")

        target_files = [
            "armor.json",
            "armaments.json",
            "talismans.json",
            "ashes-of-war.json",
            "spells.json",
        ]



        for filename in target_files:
            file_path = os.path.join(data_dir, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)

                items = list(raw_data.values()) if isinstance(raw_data, dict) else raw_data

                for data in items:
                    erdb_id = str(data.get("id"))

                    # Get and clean category
                    erdb_category = data.get("category", "").strip()

                    # Map to item type
                    item_type = ERDB_TO_ITEMTYPE.get(erdb_category, ItemType.OTHER)

                    # Debug unmapped categories
                    if item_type == ItemType.OTHER:
                        print(f"⚠️ Unmapped category: '{erdb_category}' for item: {data.get('name')}")

                    # Extract stats
                    scaling = data.get("scaling", {})
                    attack_power = data.get("attack_power", {})
                    defense = data.get("defense", {})

                    # Handle effects
                    effects = None
                    if item_type in [ItemType.TALISMAN, ItemType.SPELL, ItemType.ASH_OF_WAR]:
                        effects_data = data.get("effects", [])
                        if effects_data and isinstance(effects_data, list):
                            effects = effects_data[0] if effects_data else None

                    # Get or create item
                    obj, created = Item.objects.get_or_create(
                        erdb_id=erdb_id,
                        defaults={
                            "name": data.get("name", "Unnamed"),
                            "type": item_type,
                            "description": "\n".join(data.get("description", [])),
                            "image_url": f"https://example.com/images/{data.get('icon', '')}.png",
                            "icon": data.get("icon", ""),
                            "weight": data.get("weight", 0),
                            "effects": effects,
                            "required_stats": data.get("requirements", {}),
                            "scaling": scaling,
                            "attack_power": attack_power,
                            "defense": defense,
                            "fp_cost": data.get("fp_cost", 0),
                        }
                    )

                    # Update existing items
                    if not created:
                        update_fields = []
                        if obj.type != item_type:
                            obj.type = item_type
                            update_fields.append("type")
                        if obj.effects != effects:
                            obj.effects = effects
                            update_fields.append("effects")

                        if update_fields:
                            obj.save(update_fields=update_fields)

                self.stdout.write(self.style.SUCCESS(f"✅ {filename} imported ({len(items)} items)"))

            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"⚠️ File not found: {file_path}"))
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f"❌ Invalid JSON in {file_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {filename} failed: {str(e)}"))
