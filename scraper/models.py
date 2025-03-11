from django.db import models


class ScrapeSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")
    messages = models.JSONField(default=list)
