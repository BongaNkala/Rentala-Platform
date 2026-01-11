from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.ListingListView.as_view(), name='list'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('<int:pk>/<slug:slug>/', views.ListingDetailView.as_view(), name='detail_slug'),
    path('category/<slug:category_slug>/', views.ListingListView.as_view(), name='category'),
]
