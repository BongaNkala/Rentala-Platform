from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('listings/<uuid:pk>/', views.ListingDetailView.as_view(), name='listing_detail'),
    path('listings/<slug:slug>/', views.ListingDetailView.as_view(), name='listing_detail_slug'),
    
    # Static pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('how-it-works/', views.HowItWorksView.as_view(), name='how_it_works'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('host/dashboard/', views.HostDashboardView.as_view(), name='host_dashboard'),
]
