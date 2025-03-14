from django.contrib import admin
from .models import CustomLabel


@admin.register(CustomLabel)
class CustomLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
