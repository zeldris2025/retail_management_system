from django.db import models

class Shop(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    business_license = models.ImageField(upload_to='media/licenses/')
    shop_images = models.ImageField(upload_to='media/images/')
    
    def __str__(self):
        return self.name