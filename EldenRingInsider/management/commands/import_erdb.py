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
                    attack_power = {
                        "types": data.get("attack_attributes", []),
                        "sp_consumption": data.get("sp_consumption_rate", 0)
                    }

                    Item.objects.update_or_create(
                        erdb_id=str(data.get("id")),
                        defaults={
                            "name": data.get("name", "Unnamed"),
                            "type": item_type,
                            "description": "\n".join(data.get("description", [])),
                            "image_url": f"https://example.com/images/{data.get('icon', '')}.png",  # Adjust for images
                            "weight": data.get("weight", 0),
                            "required_stats": data.get("requirements", {}),
                            "attack_power": attack_power,
                            # "defense": {},  # Remove if I find actual defense data
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
