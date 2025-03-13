import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from .classify import classify_messages
from .utils import (configure_browser,
                    navigate_to_linkedin_and_set_cookies,
                    navigate_to_messages,
                    scroll_to_load_all_conversations,
                    scrape_conversations)


@api_view(['POST'])
@csrf_exempt
def scrape_and_classify_messages(request, *args, **kwargs):
    """
    Handles the scraping and classification of LinkedIn messages.

    This view function accepts a POST request containing LinkedIn cookies,
    scrapes the user's LinkedIn messages, and classifies them.

    Args:
        request (HttpRequest): The HTTP request object containing JSON data with LinkedIn cookies.

    Returns:
        JsonResponse: A JSON response containing the status of the operation, the scraped conversations,
        and their classifications or an error message if the operation fails.

    Raises:
        JsonResponse: If an exception occurs during the scraping or classification process, a JSON response
        with the error message and a 500 status code is returned.
    """
    if request.method == "POST":
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            cookies = data.get("cookies", [])

            # Validate cookies
            if not cookies:
                return JsonResponse({"status": "error", "error": "No cookies provided"}, status=400)

            # Configure and start the browser
            driver = configure_browser()

            # Navigate to LinkedIn and set cookies
            if not navigate_to_linkedin_and_set_cookies(driver, cookies):
                return JsonResponse({"status": "error", "error": "Invalid cookies or failed to authenticate"}, status=400)

            # Navigate to LinkedIn messages
            if not navigate_to_messages(driver):
                return JsonResponse({"status": "error", "error": "Failed to load messages page"}, status=500)

            # Scroll to load all conversations
            scroll_to_load_all_conversations(driver)

            # Scrape all conversations
            conversations = scrape_conversations(driver)

            print("Scraping complete: ", conversations)

            # Close the browser
            driver.quit()

            print(f"Scraped {len(conversations)} conversations")

            # Classify the conversations
            classified_conversations = classify_messages(conversations)
            print(classified_conversations)

            # Return the scraped and classified conversations
            return JsonResponse({"status": "success", "conversations": classified_conversations})

        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)

    return JsonResponse({"status": "error", "error": "Invalid request method"}, status=400)
