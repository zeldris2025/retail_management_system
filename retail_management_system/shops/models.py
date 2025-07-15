from django.db import models

class Shop(models.Model):
    ISLAND_CHOICES = [
        ('Upolu', 'Upolu'),
        ('Savaii', 'Savaii'),
    ]
    REGION_CHOICES = [
        ('Region 1', 'Region 1'),
        ('Region 2', 'Region 2'),
        ('Region 3', 'Region 3'),
        ('Region 4', 'Region 4'),

    ]
    
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255, blank=True, null=True, default='n/a')
    phone = models.CharField(max_length=15, blank=True, null=True, default='n/a')
    address = models.CharField(max_length=255, blank=True, null=True, default='n/a')
    island = models.CharField(max_length=50, choices=ISLAND_CHOICES, default='Upolu')
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default='Region 1')
    business_license = models.ImageField(upload_to='media/licenses/' , blank=True, null=True)
    tip_top = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class ShopImage(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media/images/' , blank=True, null=True)

    def __str__(self):
        return f"Image for {self.shop.name}"