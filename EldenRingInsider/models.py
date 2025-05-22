

# Create your models here.
# EldenRingInsider/models.py
from django.db import models
from django.contrib.postgres.indexes import GinIndex


class ItemType(models.TextChoices):
    WEAPON = 'weapon', 'Weapon'
    ARMOR = 'armor', 'Armor'
    TALISMAN = 'talisman', 'Talisman'
    SPELL = 'spell', 'Spell'
    ASH_OF_WAR = 'ash_of_war', 'Ash of War'
    CONSUMABLE = 'consumable', 'Consumable'
    OTHER = 'other', 'Other'



class Item(models.Model):
    # Core ERDB Fields
    erdb_id = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ItemType.choices, default=ItemType.OTHER)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(blank=True, null=True)

    # Common Stats
    weight = models.FloatField(null=True, blank=True)
    required_stats = models.JSONField(null=True, blank=True)  # e.g. {'strength': 10, 'dexterity': 15}

    # Scaling
    scaling = models.JSONField(null=True, blank=True)

    # Type-Specific Stats
    attack_power = models.JSONField(null=True, blank=True)  # e.g. {'physical': 120, 'magic': 80}
    defense = models.JSONField(null=True, blank=True)       # e.g. {'physical': 8.5, 'magic': 10.2}
    spell_requirements = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['name']),
            GinIndex(fields=['attack_power']),  # Creates GIN index for JSONB
            GinIndex(fields=['defense'])
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class Build(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
   # items = models.ManyToManyField('Item', blank=True)  # builds can have many items

    def __str__(self):
        return self.name



class EquipmentSlot(models.Model):
    SLOT_CHOICES = [
        ('RH1', 'Right Hand 1'),
        ('RH2', 'Right Hand 2'),
        ('LH1', 'Left Hand 1'),
        ('LH2', 'Left Hand 2'),
        ('Helms', 'Helms'),
        ('Chest Armor', 'Chest Armor'),
        ('Gauntlets', 'Gauntlets'),
        ('Greaves', 'Greaves'),
        ('Talisman1', 'Talisman Slot 1'),
        ('Talisman2', 'Talisman Slot 2'),
        ('Talisman3', 'Talisman Slot 3'),
        ('Talisman4', 'Talisman Slot 4'),
        ('Spell1', 'Spell Slot 1'),
        ('Spell2', 'Spell Slot 2'),
        ('Spell3', 'Spell Slot 3'),
        ('Spell4', 'Spell Slot 4'),
        ('AshOfWar1', 'Ash of War 1'),
        ('AshOfWar2', 'Ash of War 2'),

    ]
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name='equipment_slots')
    slot_name = models.CharField(max_length=50, choices=SLOT_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('build', 'slot_name')

    def __str__(self):
        return f"{self.build.name} - {self.get_slot_name_display()}"
