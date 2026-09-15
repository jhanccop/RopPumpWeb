from django.urls import path
from . import views

app_name = 'oilfield_wellanalyzer'

urlpatterns = [
    path('',               views.WellAnalyzerListView.as_view(),   name='list'),
    path('add/',           views.WellAnalyzerAddView.as_view(),    name='add'),
    path('<int:pk>/edit/', views.WellAnalyzerEditView.as_view(),   name='edit'),
    path('<int:pk>/',      views.WellAnalyzerDetailView.as_view(), name='detail'),
]
