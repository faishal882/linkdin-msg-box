from django.urls import path
from .views import scrape_and_classify_messages

app_name = "scraper"

urlpatterns = [
    path("scrape-messages/", scrape_and_classify_messages, name="scrape-messages"),
]
