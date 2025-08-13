# EldenRingInsider/management/commands/export_presets.py

from django.core.management.base import BaseCommand
from EldenRingInsider.models import Build, EquipmentSlot
import json

class Command(BaseCommand):
    help = 'Export all build presets to a JSON file'

    def handle(self, *args, **kwargs):
        presets = []
        for build in Build.objects.all():
            slots = {}
            for slot in build.equipment_slots.all():
                slots[slot.slot_name] = {
                    "item_id": slot.item.id if slot.item else None,
                    "item_name": slot.item.name if slot.item else None,
                    "item_type": slot.item.type if slot.item else None,
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
