from django.urls import path
from .views import scrape_and_classify_messages, create_label, fetch_labels

app_name = "scraper"

urlpatterns = [
    path("classify-messages/", scrape_and_classify_messages, name="scrape-messages"),
    path("create-label/", create_label, name="create-label"),
    path("fetch-labels/", fetch_labels, name="fetch-labels"),
]
