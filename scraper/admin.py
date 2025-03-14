from django.contrib import admin
from .models import CustomLabel, Conversation


@admin.register(CustomLabel)
class CustomLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    pass
