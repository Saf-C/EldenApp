from django.db import models

# Create your models here.
# EldenRingInsider/models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.CharField(max_length=255, default='/static/placeholder.jpg')
    type = models.CharField(max_length=50)
    #image = models.URLField()  # Uploaded images go to "media/item_images/"


    def __str__(self):
        return self.name





