from django.contrib import admin

# Register your models here.
# EldenRingInsider/admin.py
from django.contrib import admin
from .models import Item, Build, EquipmentSlot

# Register the Item model with the admin interface
#admin.site.register(Item)
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'image_url')
    #list_filter = ('type',)
   # search_fields = ('name',)

class EquipmentSlotInline(admin.TabularInline):
    model = EquipmentSlot
    extra = 5
  #  min_num = 1
 #   fields = ('slot_name', 'item',)

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
   # list_display = ('name',)
    inlines = [EquipmentSlotInline]