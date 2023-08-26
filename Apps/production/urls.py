from django.urls import path
from . import views

app_name = "production_app"

urlpatterns = [
    path('production/', views.ListOverview.as_view(),name = "overview"),
    path('production/<PumpName>', views.ListProduction.as_view(),name = 'view'),
    path('production/add/<PumpName>', views.DataCreateView.as_view(), name='add'),
    path('production/update/<PumpName>', views.DataUpdateView.as_view(), name='update'),
    path('production/remove/<PumpName>', views.DataRemoveView.as_view(), name='remove'),
    path('success/', views.SuccessView.as_view(), name='success'),

    path('production/new/', views.NewCreateView.as_view(), name='new'),
]