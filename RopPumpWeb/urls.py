"""
URL configuration for RopPumpWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #re_path('', include('Apps.batteries.urls')),
    #re_path('', include('Apps.company.urls')),
    re_path('', include('Apps.data.urls')),
    re_path('', include('Apps.device.urls')),
    re_path('', include('Apps.equipment.urls')),
    #re_path('', include('Apps.field.urls')),
    #re_path('', include('Apps.groups.urls')),
    re_path('', include('Apps.home.urls')),
    
    #re_path('', include('Apps.groups.urls')),
    #re_path('', include('Apps.home.urls')),

    #re_path('', include('Apps.overview.urls')),
    #re_path('', include('Apps.production.urls')),
    #re_path('', include('Apps.wells.urls')),
    #re_path('', include('Apps.settings.urls')),

    re_path('', include('Apps.users.urls')),
]
