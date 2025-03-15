import json

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from .classify import classify_messages
from .utils import (configure_browser,
                    navigate_to_linkedin_and_set_cookies,
                    navigate_to_messages,
                    scroll_to_load_all_conversations,
                    scrape_conversations, reclassify_all_conversations)
from .serializers import CustomLabelSerializer, ConversationSerializer, SpamCounterSerializer
from .models import CustomLabel, Conversation, SpamCounter


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
            api_key = data.get("api_key")
            num_conversations = data.get("num_conversations")

            # Validate cookies
            if not cookies:
                return JsonResponse({"status": "error", "error": "No cookies provided"}, status=400)

            # Validate cookies
            if not api_key:
                return JsonResponse({"status": "error", "error": "No Api Key provided"}, status=400)

            # Validate cookies
            if not num_conversations:
                return JsonResponse({"status": "error", "error": "No of conversations to scrap not provided"}, status=400)

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
            conversations = scrape_conversations(driver, num_conversations)

            print("Scraping complete: ", conversations)

            # Close the browser
            driver.quit()

            print(f"Scraped {len(conversations)} conversations")

            # Classify the conversations
            classified_conversation = classify_messages(conversations, api_key)

            if classified_conversation is True:
                try:
                    conversations = Conversation.objects.all()
                    serializer = ConversationSerializer(
                        conversations, many=True)
                    return Response({"status": "success", "conversations": serializer.data})
                except Exception as e:
                    return JsonResponse({"status": "error", "error": str(e)}, status=500)
            else:
                success, error = classified_conversation
                return JsonResponse({"status": "error", "error": str(error)}, status=500)

        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)

    return JsonResponse({"status": "error", "error": "Invalid request method"}, status=400)


@api_view(['POST'])
def create_label(request):
    """
    Create a new custom label.
    """
    print(request.data)
    if request.method == 'POST':
        api_key = request.data["api_key"]
        if request.data["name"] != "" and request.data["description"] != "" and api_key:
            serializer = CustomLabelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                try:
                    reclassify_all_conversations(api_key)
                except:
                    return JsonResponse({"status": "error", "error": "failed to reclassify the messages"}, status=400)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def fetch_labels(request):
    """
    Fetch all custom labels.
    """
    if request.method == 'GET':
        labels = CustomLabel.objects.all()
        serializer = CustomLabelSerializer(labels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def fetch_spam_counters(request):
    """
    Fetch spam counter data from the database.
    """
    try:
        spam_counters = SpamCounter.objects.all()
        serializer = SpamCounterSerializer(spam_counters, many=True)
        return Response({"status": "success", "spam_counters": serializer.data})

    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)}, status=500)
