from django.urls import path
from . import views

app_name = 'camera_app'

urlpatterns = [
    # Dashboard
    path('camera/', views.DashboardView.as_view(), name='dashboard'),

    # Stations
    path('camera/stations/', views.StationListView.as_view(), name='station_list'),
    path('camera/stations/add/', views.StationAddView.as_view(), name='station_add'),
    path('camera/stations/update/<pk>/', views.StationUpdateView.as_view(), name='station_update'),
    path('camera/stations/remove/<pk>/', views.StationRemoveView.as_view(), name='station_remove'),
    path('camera/stations/detail/<pk>/', views.StationDetailView.as_view(), name='station_detail'),

    # Captures
    path('camera/captures/', views.CaptureListView.as_view(), name='capture_list'),
    path('camera/captures/add/', views.CaptureAddView.as_view(), name='capture_add'),
    path('camera/captures/detail/<pk>/', views.CaptureDetailView.as_view(), name='capture_detail'),
    path('camera/captures/update/<pk>/', views.CaptureUpdateView.as_view(), name='capture_update'),
    path('camera/captures/remove/<pk>/', views.CaptureRemoveView.as_view(), name='capture_remove'),

    # Reports
    path('camera/reports/', views.ReportView.as_view(), name='report'),
]
