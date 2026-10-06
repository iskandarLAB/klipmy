from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('campaign/<int:pk>/', views.detail_view, name='detail'),
    path('campaign/new/', views.create_view, name='create'),
    path('brand/dashboard/', views.brand_dashboard_view, name='brand_dashboard'),
    path('campaign/<int:pk>/toggle/', views.toggle_status_view, name='toggle_status'),
]
