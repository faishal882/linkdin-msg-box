from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction


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
    username = models.CharField(max_length=255, null=True)
    profile_url = models.URLField(blank=True, null=True)
    messages = models.JSONField(default=list, null=True)
    last_message_timestamp = models.DateTimeField(null=True)
    label = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.username} - {self.label}"


class SpamCounter(models.Model):
    """
    Model to track the number of times a user's messages are classified as spam.
    """
    username = models.CharField(max_length=255)
    profile_url = models.URLField(
        blank=True, null=True, unique=True)
    spam_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} - Spam Count: {self.spam_count}"


# Signal to trigger reclassification when a CustomLabel is updated
# @receiver(post_save, sender=CustomLabel)
# def reclassify_conversations_on_label_update(sender, instance, **kwargs):
#     """
#     Trigger reclassification of conversations when a CustomLabel is updated.
#     """
#     print(
#         f"CustomLabel updated: {instance.name}. Reclassifying conversations...")
#     reclassify_all_conversations()


# def reclassify_all_conversations():
#     """
#     Fetch all conversations from the database, reclassify them, and update their labels.
#     """
#     from .classify import classify_messages
#     try:
#         conversations = list(Conversation.objects.all().values(
#             "thread_url", "username", "profile_url", "messages", "last_message_timestamp"
#         ))

#         if conversations:
#             classified_conversations = classify_messages(
#                 conversations, GEMINI_API_KEY)
#     except Exception as e:
#         print(f"Failed to reclassify conversations. Error: {e}")
