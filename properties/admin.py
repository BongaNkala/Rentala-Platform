from django.contrib import admin
from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'city', 'status', 'monthly_rent', 'is_active']
    list_filter = ['status', 'property_type', 'is_active']
    search_fields = ['title', 'address', 'city', 'state']
    list_editable = ['status', 'is_active']
