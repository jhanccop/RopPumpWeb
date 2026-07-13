from django.urls import path
from . import views

app_name = 'transformer_app'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Transformers
    path('transformers/', views.TransformerListView.as_view(), name='transformer_list'),
    path('transformers/add/', views.TransformerAddView.as_view(), name='transformer_add'),
    path('transformers/<int:pk>/', views.TransformerDetailView.as_view(), name='transformer_detail'),
    path('transformers/<int:pk>/edit/', views.TransformerUpdateView.as_view(), name='transformer_update'),
    path('transformers/<int:pk>/delete/', views.TransformerDeleteView.as_view(), name='transformer_remove'),

    # Substations
    path('substations/', views.SubstationListView.as_view(), name='substation_list'),
    path('substations/add/', views.SubstationAddView.as_view(), name='substation_add'),
    path('substations/<int:pk>/edit/', views.SubstationUpdateView.as_view(), name='substation_update'),
    path('substations/<int:pk>/delete/', views.SubstationDeleteView.as_view(), name='substation_remove'),

    # Readings
    path('readings/', views.ReadingListView.as_view(), name='reading_list'),
    path('readings/add/', views.ReadingAddView.as_view(), name='reading_add'),

    # Alerts
    path('alerts/', views.AlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/acknowledge/', views.AlertAcknowledgeView.as_view(), name='alert_acknowledge'),
    path('alerts/<int:pk>/close/', views.AlertCloseView.as_view(), name='alert_close'),

    # Alert Rules
    path('rules/', views.AlertRuleListView.as_view(), name='rule_list'),
    path('rules/add/', views.AlertRuleAddView.as_view(), name='rule_add'),
    path('rules/<int:pk>/edit/', views.AlertRuleUpdateView.as_view(), name='rule_update'),
    path('rules/<int:pk>/delete/', views.AlertRuleDeleteView.as_view(), name='rule_remove'),
]
