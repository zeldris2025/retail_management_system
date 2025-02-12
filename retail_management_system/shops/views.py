from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
import os
import zipfile
from django.conf import settings
from .models import Shop
from .forms import ShopForm

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

def add_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop_list')
    else:
        form = ShopForm()
    return render(request, 'shops/add_shop.html', {'form': form})

def edit_shop(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('shop_list')
    else:
        form = ShopForm(instance=shop)
    return render(request, 'shops/edit_shop.html', {'form': form, 'shop': shop})

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
            images_url = shop.shop_images.url if shop.shop_images else ''
            writer.writerow([shop.name, shop.owner, shop.phone, shop.address, license_url, images_url])
    
    zip_path = os.path.join(settings.MEDIA_ROOT, 'shops_report.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(csv_path, 'shops_report.csv')
        for shop in Shop.objects.all():
            if shop.business_license:
                zipf.write(shop.business_license.path, os.path.basename(shop.business_license.path))
            if shop.shop_images:
                zipf.write(shop.shop_images.path, os.path.basename(shop.shop_images.path))
    
    with open(zip_path, 'rb') as f:
        response.write(f.read())
    
    os.remove(csv_path)
    os.remove(zip_path)
    
    return response

