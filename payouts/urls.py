from django.urls import path
from . import views

app_name = 'payouts'

urlpatterns = [
    path('wallet/', views.wallet_view, name='wallet'),
    path('admin/list/', views.admin_payouts_view, name='admin_list'),
    path('admin/approve/<int:pk>/', views.admin_approve_view, name='admin_approve'),
]
