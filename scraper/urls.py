from django.urls import path
from .views import scrape_messages
# firecrawl_scrap

app_name = "scraper"

urlpatterns = [
    path("scrape-messages/", scrape_messages, name="scrape-messages"),
    # path("test/", test, name="test"),
    # path("firecrawl-scrap/", firecrawl_scrap, name="firecrawl-scrap"),
]
