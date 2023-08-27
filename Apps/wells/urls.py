from django.urls import path
from . import views

app_name = "wells_app"

urlpatterns = [
    path('wells/', views.ListOverview.as_view(),name = "overview"),
    path('wells/update/<pk>', views.DataUpdateView.as_view(), name='update'),
    path('wells/remove/<pk>', views.DataRemoveView.as_view(), name='remove'),
    path('success/', views.SuccessView.as_view(), name='success'),

    #path('wells/new/', views.NewCreateView.as_view(), name='new'),
]