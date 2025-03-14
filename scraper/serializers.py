from .models import CustomLabel
from rest_framework import serializers
from .models import ScrapeSession


class ScrapeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeSession
        fields = ["session_id", "status", "messages"]


class CustomLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomLabel
        fields = ['id', 'name', 'description']
