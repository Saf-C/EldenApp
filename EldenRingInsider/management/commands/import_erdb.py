# EldenRingInsider/management/commands/import_erdb.py

import json
import os
from django.core.management.base import BaseCommand
from EldenRingInsider.models import Item, ItemType

# Map ERDB categories to your ItemType choices
ERDB_TO_ITEMTYPE = {
    # Armor
    "Head": ItemType.ARMOR,
    "Body": ItemType.ARMOR,
    "Arms": ItemType.ARMOR,
    "Legs": ItemType.ARMOR,

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
                    erdb_category = data.get("category")  # Should be the specific category from ERDB
                    item_type = ERDB_TO_ITEMTYPE.get(erdb_category, ItemType.OTHER)

                    # Diagnosing categorisation of items
                    erdb_category = data.get("category")
                    item_type = ERDB_TO_ITEMTYPE.get(erdb_category, ItemType.OTHER)
                    if item_type == ItemType.OTHER:
                        print(f"Unmapped category: {erdb_category}")

                    # Extract stats as needed (example placeholders)
                    scaling = data.get("scaling", {})
                    attack_power = data.get("attack_power", {})
                    defense = data.get("defense", {})

                    obj, created = Item.objects.get_or_create(
                        erdb_id=erdb_id,
                        defaults={
                            "name": data.get("name", "Unnamed"),
                            "type": item_type,
                            "description": "\n".join(data.get("description", [])),
                            "image_url": f"https://example.com/images/{data.get('icon', '')}.png",
                            "icon": data.get("icon", ""),
                            "weight": data.get("weight", 0),
                            "required_stats": data.get("requirements", {}),
                            "scaling": scaling,
                            "attack_power": attack_power,
                            "defense": defense,
                            "spell_requirements": data.get("effects", {}),
                        }
                    )
                    if not created:
                        # Only update the type/category!
                        obj.type = item_type
                        obj.save(update_fields=["type"])

                self.stdout.write(self.style.SUCCESS(f"✅ {filename} imported ({len(items)} items)"))

            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"⚠️ File not found: {file_path}"))
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f"❌ Invalid JSON in {file_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {filename} failed: {str(e)}"))
