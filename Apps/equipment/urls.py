from django.urls import path
from . import views
from django.views.decorators.http import require_POST

app_name = "equipment_app"

urlpatterns = [
    path('equipments', views.ListOverview.as_view(),name = "equipments"),

    path('equipments/view_tank/<pk>', views.TankView.as_view(), name ='view_tank'),
    path('equipments/add_tank/', views.TankAddView.as_view(), name ='add_tank'),
    path('equipments/update_tank/<pk>', views.TankUpdateView.as_view(), name ='update_tank'),
    path('equipments/remove_tank/<pk>', views.TankRemoveView.as_view(), name ='remove_tank'),

    path('equipments/add_environmental/', views.EnvironmentalAddView.as_view(), name ='add_environmental'),
    path('equipments/update_environmental/<pk>', views.EnvironmentalUpdateView.as_view(), name ='update_environmental'),
    path('equipments/remove_environmental/<pk>', views.EnvironmentalRemoveView.as_view(), name ='remove_environmental'),

    path('equipments/view_RodPumpWell/<pk>', views.TankAddView.as_view(), name ='view_RodPumpWell'),
    path('equipments/add_RodPumpWell/', views.RodPumpWellAddView.as_view(), name ='add_RodPumpWell'),
    path('equipments/update_RodPumpWell/<pk>', views.RodPumpWellUpdateView.as_view(), name ='update_RodPumpWell'),
    path('equipments/remove_RodPumpWell/<pk>', views.RodPumpWellRemoveView.as_view(), name ='remove_RodPumpWell'),

    path('success/', views.SuccessView.as_view(), name='success'),
]