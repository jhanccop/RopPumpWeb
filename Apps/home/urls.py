from django.urls import path
from . import views

app_name = "home_app"

urlpatterns = [
    path('',views.InitView.as_view()),

    path(
            'home',
            views.InitView.as_view(),
            name = "home"
        ),

    path(
            'dispositivos',
            views.DevicesView.as_view(),
            name = "dispositivos"
        ),

    #path('login', views.LoginView.as_view()),
]
