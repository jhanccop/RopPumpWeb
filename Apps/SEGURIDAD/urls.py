from django.urls import path
from . import views

app_name = 'seguridad'

urlpatterns = [
    path('',                             views.DashboardView.as_view(),    name='dashboard'),
    path('dispositivos/',                views.DeviceListView.as_view(),   name='device_list'),
    path('dispositivos/add/',            views.DeviceAddView.as_view(),    name='device_add'),
    path('dispositivos/<int:pk>/edit/',  views.DeviceEditView.as_view(),   name='device_edit'),
    path('log/',                         views.EventLogView.as_view(),     name='event_log'),
    path('log/export/',                  views.EventLogCSVView.as_view(),  name='event_log_csv'),
    path('api/device/<int:pk>/status/',  views.DeviceStatusAPI.as_view(),  name='device_status_api'),
]
