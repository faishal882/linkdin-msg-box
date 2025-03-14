from django.db import models


class ScrapeSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")
    messages = models.JSONField(default=list)


class CustomLabel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Conversation(models.Model):
    thread_url = models.URLField(unique=True)
    username = models.CharField(max_length=255)
    profile_url = models.URLField(blank=True, null=True)  # Optional field
    messages = models.JSONField(default=list)  # List of messages as JSON
    last_message_timestamp = models.DateTimeField()  # Timestamp of the last message
    label = models.CharField(max_length=255)  # Classification label

    def __str__(self):
        return f"{self.username} - {self.label}"
