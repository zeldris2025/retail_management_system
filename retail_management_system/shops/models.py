from django.db import models

class Shop(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    business_license = models.ImageField(upload_to='media/licenses/')
    
    def __str__(self):
        return self.name

class ShopImage(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media/images/')

    def __str__(self):
        return f"Image for {self.shop.name}"