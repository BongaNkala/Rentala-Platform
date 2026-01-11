from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
