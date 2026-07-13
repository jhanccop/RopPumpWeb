from django.urls import path
from . import views

app_name = 'oilfield_app'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Batteries
    path('batteries/', views.BatteryListView.as_view(), name='battery_list'),
    path('batteries/add/', views.BatteryAddView.as_view(), name='battery_add'),
    path('batteries/<int:pk>/edit/', views.BatteryUpdateView.as_view(), name='battery_update'),
    path('batteries/<int:pk>/delete/', views.BatteryDeleteView.as_view(), name='battery_remove'),

    # Wells
    path('wells/', views.WellListView.as_view(), name='well_list'),
    path('wells/add/', views.WellAddView.as_view(), name='well_add'),
    path('wells/<int:pk>/', views.WellDetailView.as_view(), name='well_detail'),
    path('wells/<int:pk>/edit/', views.WellUpdateView.as_view(), name='well_update'),
    path('wells/<int:pk>/delete/', views.WellDeleteView.as_view(), name='well_remove'),

    # Tanks
    path('tanks/', views.TankListView.as_view(), name='tank_list'),
    path('tanks/add/', views.TankAddView.as_view(), name='tank_add'),
    path('tanks/<int:pk>/', views.TankDetailView.as_view(), name='tank_detail'),
    path('tanks/<int:pk>/edit/', views.TankUpdateView.as_view(), name='tank_update'),
    path('tanks/<int:pk>/delete/', views.TankDeleteView.as_view(), name='tank_remove'),

    # Pumping Units
    path('pumping-units/', views.PumpingUnitListView.as_view(), name='pumping_unit_list'),
    path('pumping-units/add/', views.PumpingUnitAddView.as_view(), name='pumping_unit_add'),
    path('pumping-units/<int:pk>/edit/', views.PumpingUnitUpdateView.as_view(), name='pumping_unit_update'),
    path('pumping-units/<int:pk>/delete/', views.PumpingUnitDeleteView.as_view(), name='pumping_unit_remove'),

    # Production
    path('production/', views.ProductionListView.as_view(), name='production_list'),
    path('production/add/', views.ProductionAddView.as_view(), name='production_add'),

    # Tank Readings
    path('tank-readings/add/', views.TankReadingAddView.as_view(), name='tank_reading_add'),

    # Well Events
    path('events/add/', views.WellEventAddView.as_view(), name='event_add'),

    # Alerts
    path('alerts/', views.AlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/acknowledge/', views.AlertAcknowledgeView.as_view(), name='alert_acknowledge'),
    path('alerts/<int:pk>/close/', views.AlertCloseView.as_view(), name='alert_close'),

    # Alert Rules
    path('rules/', views.AlertRuleListView.as_view(), name='rule_list'),
    path('rules/add/', views.AlertRuleAddView.as_view(), name='rule_add'),
    path('rules/<int:pk>/edit/', views.AlertRuleUpdateView.as_view(), name='rule_update'),
    path('rules/<int:pk>/delete/', views.AlertRuleDeleteView.as_view(), name='rule_remove'),

    # Report
    path('report/', views.ReportView.as_view(), name='report'),

    # Dynamometer / Well Monitor
    path('monitor/', views.WellMonitorView.as_view(), name='well_monitor'),
    path('wells/<int:pk>/dynamometer/', views.DynamometerView.as_view(), name='dynamometer'),
]
