from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from bs4 import BeautifulSoup

from .firecrawlscarpper import firecrawl_scrapper

# Directory to save HTML files
HTML_SAVE_DIR = "scraped_pages"


@csrf_exempt
@api_view(["POST"])
def test(request, *args, **kwargs):
    data = request.data
    if data:
        print(data)
        return Response({"status": "success", "message": "User logged in successfully"})
    return Response({"status": "error", "error": "Invalid request data"}, status=400)


def save_page_html(page_source, filename):
    """Save the page source to an HTML file."""
    # Create the directory if it doesn't exist
    if not os.path.exists(HTML_SAVE_DIR):
        os.makedirs(HTML_SAVE_DIR)
    file_path = os.path.join(HTML_SAVE_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(page_source)
    print(f"Saved HTML to {file_path}")

 # Find all unread conversations
    # "msg-s-event-listitem__subject (subject may exist or not)"
    # msg-s-event-listitem__body (last one latest message)


@csrf_exempt
@api_view(["POST"])
def scrape_messages(request):
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

            # Scrape unread conversations
            conversations = scrape_read_conversations(driver)

            # Close the browser
            driver.quit()

            print(conversations)

            # Return the scraped conversations
            return JsonResponse({"status": "success", "conversations": conversations})

        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=500)

    return JsonResponse({"status": "error", "error": "Invalid request method"}, status=400)


def configure_browser():
    """Configure and return a headless Chrome browser."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)


def navigate_to_linkedin_and_set_cookies(driver, cookies):
    """Navigate to LinkedIn and set cookies. Return True if successful."""
    try:
        driver.get("https://www.linkedin.com")

        # Set cookies in the browser
        for cookie in cookies:
            if all(key in cookie for key in ["name", "value", "domain"]):
                try:
                    driver.add_cookie({
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
                    })
                    print(f"Added cookie: {cookie['name']}")
                except Exception as e:
                    print(
                        f"Failed to add cookie: {cookie['name']}. Error: {e}")
            else:
                print(f"Skipping invalid cookie: {cookie}")

        return True
    except Exception as e:
        print(f"Failed to navigate to LinkedIn or set cookies. Error: {e}")
        return False


def navigate_to_messages(driver):
    """Navigate to LinkedIn messages page. Return True if successful."""
    try:
        driver.get("https://www.linkedin.com/messaging/")

        # Wait for messages to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".msg-conversations-container__conversations-list"))
        )
        return True
    except Exception as e:
        print(f"Failed to load messages page. Error: {e}")
        return False


def scrape_read_conversations(driver):
    """Scrape unread conversations and return a list of conversations."""
    conversations = []
    try:
        # Find all unread conversations
        conversation_elements = driver.find_elements(
            By.CSS_SELECTOR, ".msg-conversation-listitem")
        for index, element in enumerate(conversation_elements):
            try:
                # Click on the conversation to load the thread
                element.click()
                time.sleep(2)  # Wait for the thread to load

                # Save the conversation thread HTML
                save_page_html(driver.page_source,
                               f"conversation_{index + 1}.html")

                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Extract conversation details
                conversation = extract_conversation_details(soup)
                if conversation:
                    conversations.append(conversation)
                    print(
                        f"Scraped unread conversation {index + 1}/{len(conversation_elements)}: {conversation['username']}")

            except Exception as e:
                print(
                    f"Failed to scrape unread conversation {index + 1}. Error: {e}")

    except Exception as e:
        print(f"Failed to find unread conversations. Error: {e}")

    return conversations


def extract_conversation_details(soup):
    """Extract username, profile image, and latest message from the conversation thread."""
    try:
        # Get the username and profile image from the conversation header
        header = soup.select_one(".msg-conversation-card__header")
        if not header:
            print("Conversation header not found.")
            return None

        username = header.select_one(
            ".msg-conversation-listitem__participant-names")
        if not username:
            print("Username not found.")
            return None
        username = username.text.strip()

        profile_image = header.select_one(
            ".msg-conversation-card__profile-image")
        if not profile_image:
            print("Profile image not found.")
            profile_image = None
        else:
            profile_image = profile_image["src"]

        # Scrape the latest message in the thread
        latest_message_element = soup.select_one(
            ".msg-s-event-listitem:last-child")
        if not latest_message_element:
            print("Latest message not found.")
            return None

        # Extract sender username for the latest message
        sender = latest_message_element.select_one(
            ".msg-s-message-group__name")
        if not sender:
            print("Sender not found.")
            sender = "Unknown"
        else:
            sender = sender.text.strip()

        # Extract subject and body (if available)
        subject = latest_message_element.select_one(
            ".msg-s-event-listitem__subject")
        body = latest_message_element.select_one(".msg-s-event-listitem__body")

        # Combine subject and body into a single message
        message = ""
        if subject:
            message += f"Subject: {subject.text.strip()}\n"
        if body:
            message += body.text.strip()

        return {
            "username": username,
            "profile_image": profile_image,
            "latest_message": {
                "sender": sender,
                "message": message,
            },
        }

    except Exception as e:
        print(f"Failed to extract conversation details. Error: {e}")
        return None


def save_page_html(page_source, filename):
    """Save the page source to an HTML file."""
    # Create the directory if it doesn't exist
    if not os.path.exists(HTML_SAVE_DIR):
        os.makedirs(HTML_SAVE_DIR)
    file_path = os.path.join(HTML_SAVE_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(page_source)
    print(f"Saved HTML to {file_path}")


# @api_view(["POST"])
# def firecrawl_scrap(request, *args, **kwargs):
#     data = json.loads(request.body)
#     cookies = data.get("cookies", [])
#     if not cookies:
#         return JsonResponse({"status": "error", "error": "No cookies provided"}, status=400)

#     scrape_status, crawl_status, map_result = firecrawl_scrapper(
#         request, cookies)
#     if scrape_status and crawl_status and map_result:
#         return Response({"status": "success", "scrape_status": scrape_status, "crawl_status": crawl_status, "map_result": map_result})
#     return Response({"status": "error", "error": "Invalid request data"}, status=400)
