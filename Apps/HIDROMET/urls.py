from django.urls import path
from . import views

app_name = 'hidromet'

urlpatterns = [
    # Public (no login required)
    path('publico/',          views.PublicHydroView.as_view(),       name='public'),
    path('publico/<int:pk>/', views.PublicHydroDetailView.as_view(), name='public_detail'),

    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Stations
    path('estaciones/',                   views.StationListView.as_view(),   name='station_list'),
    path('estaciones/add/',               views.StationAddView.as_view(),    name='station_add'),
    path('estaciones/<int:pk>/',          views.StationDetailView.as_view(), name='station_detail'),
    path('estaciones/<int:pk>/editar/',   views.StationUpdateView.as_view(), name='station_update'),
    path('estaciones/<int:pk>/eliminar/', views.StationRemoveView.as_view(), name='station_remove'),

    # Readings
    path('lecturas/',     views.ReadingListView.as_view(), name='reading_list'),
    path('lecturas/add/', views.ReadingAddView.as_view(),  name='reading_add'),

    # Reports
    path('reportes/', views.ReportView.as_view(), name='report'),
]
