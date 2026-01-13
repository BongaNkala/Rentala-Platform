from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertiesView.as_view(), name='index'),
]
