from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
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
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shops_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Owner', 'Phone', 'Address'])
    for shop in Shop.objects.all():
        writer.writerow([shop.name, shop.owner, shop.phone, shop.address])
    return response
