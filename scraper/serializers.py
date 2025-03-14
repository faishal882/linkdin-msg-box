from .models import CustomLabel
from rest_framework import serializers
from .models import ScrapeSession, Conversation


class ScrapeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeSession
        fields = ["session_id", "status", "messages"]


class CustomLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomLabel
        fields = ['id', 'name', 'description']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Converts Conversation instances into JSON format.
    """
    class Meta:
        model = Conversation
        fields = [
            "id",
            "username",
            "profile_url",
            "thread_url",
            "messages",
            "last_message_timestamp",
            "label",
        ]
