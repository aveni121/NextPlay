from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns= [
    path('', views.index, name = 'index'),
    path('process', views.process, name = 'process'),
    path('loading', views.loading, name = 'loading'),
    path('results', views.results, name = 'results')
]