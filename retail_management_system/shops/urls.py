from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_list, name='shop_list'),
    path('add/', views.add_shop, name='add_shop'),
    path('delete/<int:shop_id>/', views.delete_shop, name='delete_shop'),
    path('download/', views.download_report, name='download_report'),
    path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('<int:shop_id>/edit/', views.edit_shop, name='edit_shop'),
    path('upolu/<str:region>/', views.upolu_shops, name='upolu_shops'),
    path('savaii/<str:region>/', views.savaii_shops, name='savaii_shops'),
]