# EldenRingInsider/management/commands/export_presets.py
from django.core.management.base import BaseCommand
from EldenRingInsider.models import Build, EquipmentSlot
import json


class Command(BaseCommand):
    help = 'Export all build presets to a JSON file'

    def handle(self, *args, **kwargs):
        # Define the exact slot names you want in your final export
        # This mapping ensures consistency with your HTML template
        SLOT_MAPPING = {
            'RH1': 'Right Hand 1', 'RH2': 'Right Hand 2',
            'LH1': 'Left Hand 1', 'LH2': 'Left Hand 2',
            'Helms': 'Helm', 'Chest Armor': 'Chest', 'Gauntlets': 'Gauntlets', 'Greaves': 'Greaves',
            'Talisman1': 'Talisman 1', 'Talisman2': 'Talisman 2',
            'Talisman3': 'Talisman 3', 'Talisman4': 'Talisman 4',
            'Spell1': 'Spell 1', 'Spell2': 'Spell 2', 'Spell3': 'Spell 3', 'Spell4': 'Spell 4',
            'AshOfWar1': 'Ash of War 1', 'AshOfWar2': 'Ash of War 2',
        }

        presets = []
        for build in Build.objects.all():
            slots = {}
            # Loop through the desired slot names and fetch the corresponding equipment slot
            for slot_code, _ in SLOT_MAPPING.items():
                try:
                    equipment_slot = build.equipment_slots.get(slot_name=slot_code)
                    slots[slot_code] = {
                        "item_id": equipment_slot.item.id if equipment_slot.item else None,
                        "item_name": equipment_slot.item.name if equipment_slot.item else None,
                        "item_type": equipment_slot.item.type if equipment_slot.item else None,
                    }
                except EquipmentSlot.DoesNotExist:
                    # If a slot is missing, it's represented as empty
                    slots[slot_code] = {
                        "item_id": None,
                        "item_name": None,
                        "item_type": None,
                    }

            presets.append({
                "build_id": build.id,
                "name": build.name,
                "description": build.description,
                "slots": slots,
            })

        with open("build_presets_export.json", "w") as f:
            json.dump(presets, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Exported {len(presets)} builds to build_presets_export.json"))