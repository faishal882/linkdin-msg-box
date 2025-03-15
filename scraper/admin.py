from django.contrib import admin
from .models import CustomLabel, Conversation, SpamCounter


@admin.register(CustomLabel)
class CustomLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    pass


@admin.register(SpamCounter)
class SpamCounterAdmin(admin.ModelAdmin):
    pass
