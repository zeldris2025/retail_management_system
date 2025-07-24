from django.contrib import admin
from django import forms
from .models import Shop, ShopImage, Business # Added Document import      # Added DocumentResource import (adjust path as needed)
from import_export.admin import ImportExportModelAdmin  # Added ImportExportModelAdmin import
from import_export import resources
from import_export.fields import Field
from django.utils.html import format_html      # Added format_html import
import os
import csv
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect

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

class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")

@admin.register(Shop)
class ShopAdmin(ImportExportModelAdmin):
    form = ShopAdminForm
    inlines = [ShopImageInline]
    list_display = ('name', 'owner', 'phone', 'island', 'region', 'business_license_image', 'tip_top')
    search_fields = ('name', 'owner', 'island', 'region')
    list_filter = ('island', 'region', 'name')

    def business_license_image(self, obj):
        if obj.business_license:
            return f'<img src="{obj.business_license.url}" width="100" height="100" />'
        return "No Image"
    business_license_image.allow_tags = True
    business_license_image.short_description = "Business License"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='shop_import_csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, "Uploaded file is not a CSV file.")
                    return HttpResponseRedirect(request.get_full_path())

                try:
                    decoded_file = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.DictReader(decoded_file)
                    required_fields = {'name', 'owner', 'phone', 'address'}
                    if not all(field in reader.fieldnames for field in required_fields):
                        messages.error(request, "CSV file must contain 'name', 'owner', 'phone', and 'address' columns.")
                        return HttpResponseRedirect(request.get_full_path())

                    for row in reader:
                        try:
                            # Update or create Shop instance
                            _ = Shop.objects.update_or_create(
                                name=row['name'],
                                defaults={
                                    'owner': row['owner'],
                                    'phone': row['phone'],
                                    'address': row['address'],
                                    'island': row.get('island', ''),
                                    'region': row.get('region', ''),
                                }
                            )
                        except Exception as e:
                            messages.warning(request, f"Error processing row for shop '{row.get('name', 'Unknown')}': {str(e)}")
                            continue

                    messages.success(request, "CSV file has been imported successfully.")
                    return HttpResponseRedirect('../')
                except Exception as e:
                    messages.error(request, f"Error processing CSV file: {str(e)}")
                    return HttpResponseRedirect(request.get_full_path())
        else:
            form = CsvImportForm()

        return render(request, 'admin/shop_csv_import.html', {'form': form})
    
class ShopResource(resources.ModelResource):
    # Adjust these fields according to your actual Shop model fields
    name = Field(attribute='name', column_name='name')
    owner = Field(attribute='owner', column_name='owner')
    phone = Field(attribute='phone', column_name='phone')
    address = Field(attribute='address', column_name='address')
    island = Field(attribute='island', column_name='island')
    region = Field(attribute='region', column_name='region')
    pdf_file = Field(attribute='pdf_file', column_name='pdf_file')
    pdf_file_samoan = Field(attribute='pdf_file_samoan', column_name='pdf_file_samoan')

    class Meta:
        model = Shop
        fields = ('name', 'owner', 'phone', 'address', 'island', 'region', 'pdf_file', 'pdf_file_samoan')
        import_id_fields = ('name',)
        skip_unchanged = True
        report_skipped = True

class ShopAdmin(ImportExportModelAdmin):
    resource_class = ShopResource
    list_display = ('name', 'owner', 'phone', 'address', 'island', 'region', 'pdf_file_link', 'pdf_file_samoan_link')
    list_filter = ('island', 'region')
    search_fields = ('name', 'owner', 'phone', 'address')

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_type', 'location', 'business_license', 'created_at')
    list_filter = ('business_type', 'created_at')
    search_fields = ('name', 'location', 'business_license')
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'business_type', 'island', 'location', 'picture','business_license')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )