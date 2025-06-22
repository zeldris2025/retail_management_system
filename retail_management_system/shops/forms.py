from django import forms
from django.forms import inlineformset_factory
from .models import Shop, ShopImage

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'owner', 'phone', 'address', 'business_license']

ShopImageFormSet = inlineformset_factory(
    Shop,
    ShopImage,
    fields=['image'],
    extra=2,  # Number of empty image upload fields
    can_delete=True  # Allows deleting existing images
)