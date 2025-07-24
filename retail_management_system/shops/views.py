from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
import os
import zipfile
from django.conf import settings
from .models import Shop, ShopImage, Business
from .forms import ShopForm, ShopImageFormSet
from django.db.models import Q

def shop_list(request):
    query = request.GET.get('q')
    shops = Shop.objects.all()
    if query:
        shops = shops.filter(name__icontains=query)
    
    paginator = Paginator(shops, 6)  # Show 6 shops per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shops/shop_list.html', {'page_obj': page_obj})

def upolu_shops(request, region):
    query = request.GET.get('q')
    tip_top = request.GET.get('tip_top')
    
    shops = Shop.objects.filter(island='Upolu', region=region)
    
    if query:
        shops = shops.filter(name__icontains=query)
    if tip_top is not None:
        if tip_top == '1':
            shops = shops.filter(tip_top=True)
        elif tip_top == '0':
            shops = shops.filter(tip_top=False)
    
    paginator = Paginator(shops, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shops/upolu_shops.html', {'page_obj': page_obj, 'region': region})

def savaii_shops(request, region):
    query = request.GET.get('q')
    tip_top = request.GET.get('tip_top')
    
    shops = Shop.objects.filter(island='Savaii', region=region)
    
    if query:
        shops = shops.filter(name__icontains=query)
    if tip_top is not None:
        if tip_top == '1':
            shops = shops.filter(tip_top=True)
        elif tip_top == '0':
            shops = shops.filter(tip_top=False)
    
    paginator = Paginator(shops, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shops/savaii_shops.html', {'page_obj': page_obj, 'region': region})

def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    return render(request, 'shops/shop_detail.html', {'shop': shop})

def business_list(request):
    businesses = Business.objects.all()
    
    # Get filter and search parameters from GET request
    island = request.GET.get('island', '')
    business_type = request.GET.get('business_type', '')
    search_query = request.GET.get('search_query', '')
    
    # Apply filters
    if island:
        businesses = businesses.filter(island=island)
    if business_type:
        businesses = businesses.filter(business_type=business_type)
    if search_query:
        businesses = businesses.filter(Q(name__icontains=search_query))
    
    businesses = businesses.order_by('name')
    
    # Get distinct islands and business types for filter dropdowns
    islands = Business.objects.values('island').distinct()
    business_types = Business.BUSINESS_TYPES
    
    context = {
        'businesses': businesses,
        'islands': islands,
        'business_types': business_types,
        'selected_island': island,
        'selected_business_type': business_type,
        'search_query': search_query,
    }
    return render(request, 'shops/business_list.html', context)

def add_shop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES)
        image_formset = ShopImageFormSet(request.POST, request.FILES, instance=Shop())
        if form.is_valid():
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
        if form.is_valid():
            shop = form.save()
            image_formset.instance = shop
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
        writer.writerow(['Name', 'Owner', 'Phone', 'Address', 'Island', 'Region', 'Business License', 'Shop Images'])
        for shop in Shop.objects.all():
            license_url = shop.business_license.url if shop.business_license else ''
            image_urls = '; '.join([img.image.url for img in shop.images.all()]) if shop.images.exists() else ''
            writer.writerow([shop.name, shop.owner, shop.phone, shop.address, shop.island, shop.region, license_url, image_urls])
    
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