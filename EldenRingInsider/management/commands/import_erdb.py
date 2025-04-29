import json
import os
from django.core.management.base import BaseCommand
from EldenRingInsider.models import Item, ItemType


class Command(BaseCommand):
    help = 'Import Elden Ring items from ERDB-generated JSON files'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join("data", "1.10.0")

        category_mapping = {
            "armor": ItemType.ARMOR,
            "armaments": ItemType.WEAPON,
            "talismans": ItemType.TALISMAN,
            "ashes-of-war": ItemType.ASH_OF_WAR,
            "spells": ItemType.SPELL,
            "spirit-ashes": ItemType.OTHER,
            "tools": ItemType.OTHER,
        }

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

                # Handle both dictionary and list structures
                items = list(raw_data.values()) if isinstance(raw_data, dict) else raw_data
                category = filename.replace(".json", "")
                item_type = category_mapping.get(category, ItemType.OTHER)

                for data in items:
                    # Map ERDB fields to my model
                    # Extract nested stats
                    scaling = data.get("scaling", {})
                    guard = data.get("guard", {})
                    resistance = data.get("resistance", {})
                    damage = data.get("damage", {})
                    correction_calc = data.get("correction_calc_id", {})
                    status_effects = data.get("status_effects", {})

                    # Build attack power data
                    attack_power = {
                        "base_damage": {
                            "physical": damage.get("physical", 0),
                            "magic": damage.get("magic", 0),
                            "holy": damage.get("holy", 0),
                            "lightning": damage.get("lightning", 0),
                            "fire": damage.get("fire", 0),
                            "stamina": damage.get("stamina", 0)
                        },
                        "scaling": scaling,  # Raw scaling data
                            "correction_attack_id": data.get("correction_attack_id"),
                            "correction_calc_id": correction_calc,
                            "status_effects": {
                            "bleed": status_effects.get("bleed", 0),
                            "frostbite": status_effects.get("frostbite", 0),
                            "poison": status_effects.get("poison", 0),
                            "scarlet_rot": status_effects.get("scarlet_rot", 0),
                            "sleep": status_effects.get("sleep", 0),
                            "madness": status_effects.get("madness", 0)
                        }
                    }

                    # Build defense data
                    defense = {
                        "guard": {
                            "physical": guard.get("physical", 0),
                            "magic": guard.get("magic", 0),
                            "fire": guard.get("fire", 0),
                            "lightning": guard.get("lightning", 0),
                            "holy": guard.get("holy", 0),
                            "guard_boost": guard.get("guard_boost", 0)
                        },
                        "resistances": {
                            "bleed": resistance.get("bleed", 0),
                            "poison": resistance.get("poison", 0),
                            "scarlet_rot": resistance.get("scarlet_rot", 0),
                            "frostbite": resistance.get("frostbite", 0),
                            "sleep": resistance.get("sleep", 0),
                            "madness": resistance.get("madness", 0),
                            "death_blight": resistance.get("death_blight", 0),
                            "poise": resistance.get("poise", 0)
                        }
                    }

                    Item.objects.update_or_create(
                        erdb_id=str(data.get("id")),
                        defaults={
                            "name": data.get("name", "Unnamed"),
                            "type": item_type,
                            "description": "\n".join(data.get("description", [])),
                            "image_url": f"https://example.com/images/{data.get('icon', 'icon_fem', '')}.png",  # Adjust for images
                            "weight": data.get("weight", 0),
                            "required_stats": data.get("requirements", {}),
                            "attack_power": attack_power,
                            "defense": defense,
                            "spell_requirements": data.get("effects", {}),
                        }
                    )

                self.stdout.write(self.style.SUCCESS(f"✅ {filename} imported ({len(items)} items)"))

            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"⚠️ File not found: {file_path}"))
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f"❌ Invalid JSON in {file_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {filename} failed: {str(e)}"))
