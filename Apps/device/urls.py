from django.urls import path
from . import views
from django.views.decorators.http import require_POST

app_name = "device_app"

urlpatterns = [
    path('devices', views.ListOverview.as_view(),name = "devices"),

    path('devices/add_tank/', views.TankAddView.as_view(), name ='add_tank'),
    path('devices/update_tank/<pk>', views.TankUpdateView.as_view(), name ='update_tank'),
    path('devices/remove_tank/<pk>', views.TankRemoveView.as_view(), name ='remove_tank'),

    path('devices/add_environmental/', views.EnvironmentalAddView.as_view(), name ='add_environmental'),
    path('devices/update_environmental/<pk>', views.EnvironmentalUpdateView.as_view(), name ='update_environmental'),
    path('devices/remove_environmental/<pk>', views.EnvironmentalRemoveView.as_view(), name ='remove_environmental'),

    path('devices/add_analyzer/', views.AnalyzerAddView.as_view(), name ='add_analyzer'),
    path('devices/update_analyzer/<pk>', views.AnalyzerUpdateView.as_view(), name ='update_analyzer'),
    path('devices/remove_analyzer/<pk>', views.AnalyzerRemoveView.as_view(), name ='remove_analyzer'),
    
    path('success/', views.SuccessView.as_view(), name='success'),
    #path('devices/<TankName>', views.ListTank.as_view()),
]