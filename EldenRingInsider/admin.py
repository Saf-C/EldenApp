

# Register your models here.
# EldenRingInsider/admin.py
from django.contrib import admin
from .models import Item, Build, EquipmentSlot
import json

# Register the Item model with the admin interface
#admin.site.register(Item)
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'image_url', 'icon', 'attack_power_short', 'defense_short')
    search_fields = ['name', 'type', 'description']

    def attack_power_short(self, obj):
        return f"{obj.attack_power['base_damage']['physical']} Phys"

    def defense_short(self, obj):
        return f"{obj.defense['guard']['physical']} Guard"

    @admin.display(description="Physical Attack Power")
    def attack_power_short(self, obj):
        ap = obj.attack_power or {}
        # Handle both dict and serialized JSON string
        if isinstance(ap, str):
            try:
                ap = json.loads(ap)
            except Exception:
                return "-"
        base = ap.get('base_damage', {})
        if isinstance(base, dict):
            physical = base.get('physical')
        else:
            physical = None
        return f"{physical} Phys" if physical is not None else "-"

    @admin.display(description="Physical Guard")
    def defense_short(self, obj):
        dp = obj.defense or {}
        # Defensive for JSON string as well
        if isinstance(dp, str):
            try:
                dp = json.loads(dp)
            except Exception:
                return "-"
        guard = dp.get('guard', {})
        if isinstance(guard, dict):
            physical = guard.get('physical')
        else:
            physical = None
        return f"{physical} Guard" if physical is not None else "-"


class EquipmentSlotInline(admin.TabularInline):
    model = EquipmentSlot
    extra = 5
    autocomplete_fields = ['item']


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
   # list_display = ('name',)
    inlines = [EquipmentSlotInline]


