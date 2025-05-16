

# Register your models here.
# EldenRingInsider/admin.py
from django.contrib import admin
from .models import Item, Build, EquipmentSlot

# Register the Item model with the admin interface
#admin.site.register(Item)
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'image_url', 'attack_power_short', 'defense_short')
    search_fields = ['name', 'type', 'description']

    def attack_power_short(self, obj):
        return f"{obj.attack_power['base_damage']['physical']} Phys"

    def defense_short(self, obj):
        return f"{obj.defense['guard']['physical']} Guard"


class EquipmentSlotInline(admin.TabularInline):
    model = EquipmentSlot
    extra = 5
    autocomplete_fields = ['item']


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
   # list_display = ('name',)
    inlines = [EquipmentSlotInline]