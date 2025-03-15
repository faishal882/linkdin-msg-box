from django.urls import path
from .views import scrape_and_classify_messages, create_label, fetch_labels, fetch_spam_counters

app_name = "scraper"

urlpatterns = [
    path("classify-messages/", scrape_and_classify_messages, name="scrape-messages"),
    path("create-label/", create_label, name="create-label"),
    path("fetch-labels/", fetch_labels, name="fetch-labels"),
    path("fetch-spam-count/", fetch_spam_counters, name="fetch-spam-count")
]
