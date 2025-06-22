from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
import os
import zipfile
from django.conf import settings
from .models import Shop, ShopImage
from .forms import ShopForm, ShopImageFormSet

def shop_list(request):
    query = request.GET.get('q')
    shops = Shop.objects.all()
    if query:
        shops = shops.filter(name__icontains=query)
    
    paginator = Paginator(shops, 6)  # Show 6 shops per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shops/shop_list.html', {'page_obj': page_obj})

def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    return render(request, 'shops/shop_detail.html', {'shop': shop})

# Relevant parts of views.py
from .forms import ShopForm, ShopImageFormSet

def add_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        image_formset = ShopImageFormSet(request.POST, request.FILES, instance=Shop())
        if form.is_valid() and image_formset.is_valid():
            shop = form.save()
            image_formset.instance = shop
            image_formset.save()
            return redirect('shop_list')
    else:
        form = ShopForm()
        image_formset = ShopImageFormSet(instance=Shop())
    return render(request, 'shops/add_shop.html', {'form': form, 'image_formset': image_formset})

def edit_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == 'POST':
        if 'delete' in request.POST:
            shop.delete()
            return redirect('shop_list')
        
        form = ShopForm(request.POST, request.FILES, instance=shop)
        image_formset = ShopImageFormSet(request.POST, request.FILES, instance=shop)
        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()
            return redirect('shop_list')
    else:
        form = ShopForm(instance=shop)
        image_formset = ShopImageFormSet(instance=shop)
    return render(request, 'shops/edit_shop.html', {'form': form, 'image_formset': image_formset, 'shop': shop})


def delete_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    shop.delete()
    return redirect('shop_list')

def download_report(request):
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="shops_report.zip"'
    
    csv_path = os.path.join(settings.MEDIA_ROOT, 'shops_report.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Owner', 'Phone', 'Address', 'Business License', 'Shop Images'])
        for shop in Shop.objects.all():
            license_url = shop.business_license.url if shop.business_license else ''
            # Collect all image URLs for the shop
            image_urls = '; '.join([img.image.url for img in shop.images.all()]) if shop.images.exists() else ''
            writer.writerow([shop.name, shop.owner, shop.phone, shop.address, license_url, image_urls])
    
    zip_path = os.path.join(settings.MEDIA_ROOT, 'shops_report.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_path, 'shops_report.csv')
        for shop in Shop.objects.all():
            if shop.business_license and os.path.exists(shop.business_license.path):
                zipf.write(shop.business_license.path, os.path.join('licenses', os.path.basename(shop.business_license.path)))
            for img in shop.images.all():
                if os.path.exists(img.image.path):
                    zipf.write(img.image.path, os.path.join('images', os.path.basename(img.image.path)))
    
    with open(zip_path, 'rb') as f:
        response.write(f.read())
    
    os.remove(csv_path)
    os.remove(zip_path)
    
    return response