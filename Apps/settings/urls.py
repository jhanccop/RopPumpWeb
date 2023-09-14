from django.urls import path
from . import views

app_name = "devices_app"

urlpatterns = [
    path('devices/', views.ListOverview.as_view(),name = "overview"),
    path('devices/new/', views.NewCreateView.as_view(), name='new'),
    path('devices/update/<pk>', views.DataUpdateView.as_view(), name='update'),
    path('devices/remove/<pk>', views.DataRemoveView.as_view(), name='remove'),
    path('success/', views.SuccessView.as_view(), name='success'),
]