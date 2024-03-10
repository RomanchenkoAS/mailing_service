from django.urls import path

from .views import *

urlpatterns = [
    path('', DispatchListView.as_view(), name='dispatch-list'),
    path('<int:pk>/', DispatchDetailView.as_view(), name='dispatch-detail'),
    path('<int:pk>/action/', dispatch_action_view, name='dispatch_action'),
    path('<int:dispatch_id>/stats/', real_time_stats, name='real_time_stats'),
]
