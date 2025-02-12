from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_list, name='shop_list'),
    path('add/', views.add_shop, name='add_shop'),
    path('delete/<int:shop_id>/', views.delete_shop, name='delete_shop'),
    path('download/', views.download_report, name='download_report'),

]
