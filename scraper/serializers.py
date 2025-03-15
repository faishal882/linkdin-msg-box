from .models import CustomLabel
from rest_framework import serializers
from .models import ScrapeSession, Conversation, SpamCounter


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


class SpamCounterSerializer(serializers.ModelSerializer):
    """
    Serializer for the SpamCounter model.
    """
    class Meta:
        model = SpamCounter
        fields = ["username", "profile_url", "spam_count"]
