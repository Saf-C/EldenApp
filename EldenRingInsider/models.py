from django.db import models

# Create your models here.
# EldenRingInsider/models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name




