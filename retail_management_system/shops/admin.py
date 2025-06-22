from django.contrib import admin
from django import forms
from .models import Shop, ShopImage
import os

# Inline admin for ShopImage
class ShopImageInline(admin.TabularInline):
    model = ShopImage
    extra = 1
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"

class ShopAdminForm(forms.ModelForm):
    clear_business_license = forms.BooleanField(required=False, label="Remove Business License")

    class Meta:
        model = Shop
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('clear_business_license') and instance.business_license:
            if os.path.exists(instance.business_license.path):
                os.remove(instance.business_license.path)
            instance.business_license = None
        if commit:
            instance.save()
        return instance

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    form = ShopAdminForm
    inlines = [ShopImageInline]
    list_display = ('name', 'owner', 'phone', 'business_license_image')  # Removed shop_images
    search_fields = ('name', 'owner')
    list_filter = ('name',)

    def business_license_image(self, obj):
        if obj.business_license:
            return f'<img src="{obj.business_license.url}" width="100" height="100" />'
        return "No Image"
    business_license_image.allow_tags = True
    business_license_image.short_description = "Business License"