from django.db import models

# Create your models here.
# EldenRingInsider/models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.CharField(max_length=255, default='/static/placeholder.jpg')
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Build(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class EquipmentSlot(models.Model):
    SLOT_CHOICES = [
        ('RH1', 'Right Hand 1'),
        ('LH1', 'Left Hand 1'),
        ('Helmet', 'Helmet'),
        ('Armor', 'Armor'),
        ('Gauntlets', 'Gauntlets'),
        ('Boots', 'Boots'),
        ('Talisman1', 'Talisman Slot 1'),
        ('Talisman2', 'Talisman Slot 2'),
        ('Talisman3', 'Talisman Slot 3'),
        ('Talisman4', 'Talisman Slot 4'),
        ('Flask1', 'Flask Slot 1'),
        ('Flask2', 'Flask Slot 2'),
        ('Flask3', 'Flask Slot 3'),
    ]

    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name='equipment_slots')
    slot_name = models.CharField(max_length=20, choices=SLOT_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.slot_name} - {self.item.name if self.item else 'Empty'}"




