from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:campaign_id>/', views.checkout_view, name='checkout'),
    path('mock/<str:reference>/', views.mock_checkout_view, name='mock_checkout'),
    path('callback/', views.chip_callback_view, name='callback'),
    path('return/', views.return_page_view, name='return_page'),
]
