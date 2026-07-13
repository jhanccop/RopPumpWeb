from django.urls import path
from . import views

app_name = 'weather_app'

urlpatterns = [
    # Public (no login required)
    path('fauna/weather/', views.PublicWeatherView.as_view(), name='public_weather'),
    path('fauna/weather/<int:pk>/', views.PublicWeatherDetailView.as_view(), name='public_weather_detail'),

    # Dashboard
    path('weather/', views.DashboardView.as_view(), name='dashboard'),

    # Stations
    path('weather/stations/', views.StationListView.as_view(), name='station_list'),
    path('weather/stations/add/', views.StationAddView.as_view(), name='station_add'),
    path('weather/stations/update/<pk>/', views.StationUpdateView.as_view(), name='station_update'),
    path('weather/stations/remove/<pk>/', views.StationRemoveView.as_view(), name='station_remove'),
    path('weather/stations/detail/<pk>/', views.StationDetailView.as_view(), name='station_detail'),

    # Readings
    path('weather/readings/', views.ReadingListView.as_view(), name='reading_list'),
    path('weather/readings/add/', views.ReadingAddView.as_view(), name='reading_add'),

    # Reports
    path('weather/reports/', views.ReportView.as_view(), name='report'),
]
