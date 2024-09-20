from django.urls import path
from . import views
from django.views.decorators.http import require_POST

app_name = "data_app"

urlpatterns = [
    path('data', views.ListOverview.as_view(),name = "data"),
    #path('overview/socker-rod-pump/<PumpName>', views.ListDataRodPump.as_view()),
    #path('data/socker-rod-pump/<PumpName>', views.ListDataRodPump.as_view()),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('data-tank/<TankName>', views.ListTank.as_view(), name='data-tank'),
    path('data-sensor/<EnvironmentalName>', views.ListSensor.as_view(), name='data-sensor'),
    path('data-camera/detail/<pk>', views.DetailCamera.as_view(), name='data-camera-detail'),
    path('data-camera/<VisualSamplingPointName>', views.ListCamera.as_view(), name='data-camera'),
    path('data-rod-pump/<WellName>', views.ListTank.as_view(), name='data-rod-pump'),
]