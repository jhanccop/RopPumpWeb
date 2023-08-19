from django.urls import path
from . import views
from django.views.decorators.http import require_POST

app_name = "overview_app"

urlpatterns = [
    path('overview', views.ListOverview.as_view(),name = "overview"),
    #path('overview/socker-rod-pump/<PumpName>', views.ListDataRodPump.as_view()),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('overview/<PumpName>', views.ListDataRodPump.as_view()),
]
