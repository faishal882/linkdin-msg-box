from django.urls import path
from .views import scrape_messages

app_name = "scraper"

urlpatterns = [
    path("scrape-messages/", scrape_messages, name="scrape-messages"),
]
