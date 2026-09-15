from django.urls import path
from . import views

app_name = 'oilfield_tank'

urlpatterns = [
    path('',                        views.TankStationListView.as_view(),   name='list'),
    path('add/',                    views.TankStationAddView.as_view(),    name='add'),
    path('<int:pk>/edit/',          views.TankStationEditView.as_view(),   name='edit'),
    path('<int:pk>/',               views.TankStationDetailView.as_view(), name='detail'),
    path('<int:pk>/readings/json/', views.TankReadingsAPI.as_view(),       name='readings_api'),
]
