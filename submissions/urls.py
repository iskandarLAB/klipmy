from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('submit/<int:campaign_id>/', views.submit_clip_view, name='submit'),
    path('my-clips/', views.my_clips_view, name='my_clips'),
    path('sync/<int:pk>/', views.sync_clip_view, name='sync'),
    path('sync-all/', views.sync_all_views_view, name='sync_all'),
]
