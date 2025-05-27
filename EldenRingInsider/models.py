# EldenRingInsider/models.py

from django.db import models
from django.contrib.postgres.indexes import GinIndex

class ItemType(models.TextChoices):
    # Weapon sub categorie
    # shield types
    SMALL_SHIELD = 'small_shield', 'Small Shield'
    MEDIUM_SHIELD = 'medium_shield', 'Medium Shield'
    GREATSHIELD = 'greatshield', 'Greatshield'
    # Staves
    STAFF = 'staff', 'Staff'
    GLINTSTONE_STAFF = 'glintstone_staff', 'Glintstone Staff'
    SACRED_SEAL = 'sacred_seal', 'Sacred Seal'
    # Ranged
    BALLISTA = 'ballista', 'Ballista'
    CROSSBOW = 'crossbow', 'Crossbow'
    BOW = 'bow', 'Bow'
    LIGHT_BOW = 'light_bow', 'Light Bow'
    GREATBOW = 'greatbow', 'Greatbow'
    # Melee
    KATANA = 'katana', 'Katana'
    GREAT_KATANA = 'great_katana', 'Great Katana'
    GREATSWORD = 'greatsword', 'Greatsword'
    COLOSSAL_SWORD = 'colossal_sword', 'Colossal Sword'
    COLOSSAL_WEAPON = 'colossal_weapon', 'Colossal Weapon'
    CURVED_SWORD = 'curved_sword', 'Curved Sword'
    STRAIGHTSWORD = 'straightsword', 'Straight Sword'
    DAGGER = 'dagger', 'Dagger'
    TWINBLADE = 'twinblade', 'Twinblade'
    AXE = 'axe', 'Axe'
    GREAT_AXE = 'great_axe', 'Great Axe'
    HAMMER = 'hammer', 'Hammer'
    GREAT_HAMMER = 'great_hammer', 'Great Hammer'
    FLAIL = 'flail', 'Flail'
    SPEAR = 'spear', 'Spear'
    SHORT_SPEAR = 'short_spear', 'Short Spear'
    GREAT_SPEAR = 'great_spear', 'Great Spear'
    HALBERD = 'halberd', 'Halberd'
    HEAVY_THRUSTING_SWORD = 'heavy_thrusting_sword', 'Heavy Thrusting Sword'
    THRUSTING_SWORD = 'thrusting_sword', 'Thrusting Sword'
    CLAW = 'claw', 'Claw'
    FISTS = 'fists', 'Fists'
    BACKHAND_BLADE = 'backhand_blade', 'Backhand Blade'
    REAPER = 'reaper', 'Reaper'
    WHIP = 'whip', 'Whip'
    # Torches
    TORCH = 'torch', 'Torch'


    # Other item types
    ARMOR = 'armor', 'Armor'
    TALISMAN = 'talisman', 'Talisman'
    SPELL = 'spell', 'Spell'
    ASH_OF_WAR = 'ash_of_war', 'Ash of War'
    CONSUMABLE = 'consumable', 'Consumable'
    OTHER = 'other', 'Other'

class Item(models.Model):
    erdb_id = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=32, choices=ItemType.choices, default=ItemType.OTHER)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(blank=True, null=True)

    weight = models.FloatField(null=True, blank=True)
    required_stats = models.JSONField(null=True, blank=True)
    scaling = models.JSONField(null=True, blank=True)
    attack_power = models.JSONField(null=True, blank=True)
    defense = models.JSONField(null=True, blank=True)
    spell_requirements = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['name']),
            GinIndex(fields=['attack_power']),
            GinIndex(fields=['defense'])
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class Build(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

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
