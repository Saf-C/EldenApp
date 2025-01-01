from django.db import models

# Create your models here.
# EldenRingInsider/models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=50)
    # Add other relevant fields (e.g., attack stats, magic, etc.)

    def __str__(self):
        return self.name



