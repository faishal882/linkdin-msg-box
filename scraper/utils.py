from dateutil import parser
import time
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .models import Conversation


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


def scroll_to_load_all_conversations(driver):
    """Scroll down to load all conversations."""
    try:
        # Get the conversation list container
        conversation_list = driver.find_element(
            By.CSS_SELECTOR, ".msg-conversations-container__conversations-list")

        # Scroll until no more conversations are loaded
        last_height = driver.execute_script(
            "return arguments[0].scrollHeight", conversation_list)
        while True:
            # Scroll down to the bottom of the conversation list
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", conversation_list)
            time.sleep(2)  # Wait for new conversations to load

            # Calculate new scroll height
            new_height = driver.execute_script(
                "return arguments[0].scrollHeight", conversation_list)
            if new_height == last_height:
                break  # No more conversations to load
            last_height = new_height

        print("All conversations loaded.")
    except Exception as e:
        print(f"Failed to scroll and load conversations. Error: {e}")


def scrape_conversations(driver, num_conversation=20):
    """Scrape all conversations and return a list of conversations."""
    conversations = []
    try:
        # Find all conversation elements
        conversation_elements = driver.find_elements(
            # Limit to 10 conversations
            By.CSS_SELECTOR, ".msg-conversation-listitem")
        # Number of conversation thread to scrap
        total_conversations = len(conversation_elements)
        print(f"Total conversations found: {total_conversations}")
        if total_conversations <= num_conversation:
            num_conversation = total_conversations

        for index, element in enumerate(conversation_elements[:num_conversation]):
            try:
                # Click on the conversation to load the thread
                element.click()
                time.sleep(2)  # Wait for the thread to load

                thread_url = driver.current_url
                print("Thread URL: ", thread_url)

                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Extract conversation details
                conversation = extract_conversation_details(soup, thread_url)
                if conversation:
                    try:
                        conv_thread = Conversation.objects.get(
                            thread_url=thread_url)
                        db_timestamp = conv_thread.last_message_timestamp
                        scraped_timestamp = datetime.fromisoformat(
                            conversation["last_message_timestamp"])
                        # Convert to timezone-aware (UTC)
                        scraped_timestamp = make_aware(scraped_timestamp)
                        scraped_timestamp = truncate_microseconds(
                            scraped_timestamp)

                        if db_timestamp == scraped_timestamp:
                            print("Latest Conversation in DB")
                            return conversations
                    except:
                        print("conversation object doesnot exist")

                    conversations.append(conversation)
                    print(
                        f"Scraped conversation {index + 1}/{len(conversation_elements)}: {conversation['username']}")

            except Exception as e:
                print(f"Failed to scrape conversation {index + 1}. Error: {e}")

    except Exception as e:
        print(f"Failed to find conversations. Error: {e}")

    return conversations


def extract_conversation_details(soup, thread_url):
    """Extract username, profile image, and messages from the conversation thread."""
    try:
        # extract username
        username_element = soup.find("h2", {"id": "thread-detail-jump-target"})
        if username_element:
            username = username_element.text.strip()
        else:
            username = "Unknown"

        # Extract profile URL
        profile_link_element = soup.find(
            "a", class_="msg-thread__link-to-profile")
        if profile_link_element and "href" in profile_link_element.attrs:
            profile_url = profile_link_element["href"]
        else:
            profile_url = "Not Found"

        # extract last message time
        try:
            # time header
            time_header_elements = soup.find_all(
                "time", class_="msg-s-message-list__time-heading")
            time_header = time_header_elements[-1].text.strip()
            # time stamp
            last_message_timestamp_elements = soup.find_all(
                "time", class_="msg-s-message-group__timestamp")
            last_message_timestamp = last_message_timestamp_elements[-1].text.strip(
            )

        except:
            time_header = None
            last_message_timestamp = None

        # Combine time header and last message timestamp into a single timestamp
        last_message_timestamp_combined = combine_time_header_and_timestamp(
            time_header, last_message_timestamp
        )
        print(last_message_timestamp_combined)
        # extracts messages
        messages = []
        message_elements = soup.select(".msg-s-event-listitem__body")
        for msg_element in message_elements:
            message = msg_element.text.strip()
            messages.append(message)

        return {
            "username": username,
            "profile_url": profile_url,
            "thread_url": thread_url,
            "messages": messages,
            "last_message_timestamp": last_message_timestamp_combined,
        }
    except Exception as e:
        print(f"Failed to extract conversation details. Error: {e}")
        return None


def combine_time_header_and_timestamp(time_header, last_message_timestamp):
    """
    Combine the time header (e.g. format, "Thursday", "Feb 6", "Nov 7, 2024") 
    and last message timestamp (e.g., "1:37 PM") into a single datetime object.
    Handles case insensitivity for month/day names and AM/PM designations.
    """
    try:
        # Define current date and time
        now = datetime.now()

        # Normalize time_header to lowercase for consistency
        time_header = time_header.strip().lower()

        # Initialize the date variable
        date = None

        # Handle "Today" and "Yesterday"
        if time_header == "today":
            date = now.date()
        elif time_header == "yesterday":
            date = (now - timedelta(days=1)).date()

        # Handle weekdays (e.g., "thursday")
        elif time_header in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            days_map = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
            }
            today_weekday = now.weekday()
            target_weekday = days_map.get(time_header)
            if target_weekday is not None:
                delta_days = (today_weekday - target_weekday) % 7
                date = (now - timedelta(days=delta_days)).date()

        # Handle short date formats (e.g., "feb 6")
        elif len(time_header.split()) == 2:
            try:
                # Parse the month and day (case-insensitive)
                parsed_date = parser.parse(time_header)
                # Assume the year is the current year
                date = parsed_date.replace(year=now.year).date()
            except ValueError:
                print(f"Failed to parse short date format: {time_header}")
                date = now.date()  # Default to today if parsing fails

        # Handle full date formats (e.g., "nov 7, 2024")
        elif len(time_header.split()) == 3:
            try:
                # Parse the full date (case-insensitive)
                parsed_date = parser.parse(time_header)
                date = parsed_date.date()
            except ValueError:
                print(f"Failed to parse full date format: {time_header}")
                date = now.date()  # Default to today if parsing fails

        # Default to today if no valid format is matched
        else:
            date = now.date()

        # Normalize last_message_timestamp to lowercase for case-insensitive AM/PM handling
        last_message_timestamp = last_message_timestamp.strip().lower()

        # Parse the last message timestamp
        time_format = "%I:%M %p"  # Example: "1:37 pm"
        parsed_time = datetime.strptime(
            last_message_timestamp, time_format).time()

        # Combine date and time into a single datetime object
        combined_datetime = datetime.combine(date, parsed_time)

        # Convert to ISO format for consistency
        return combined_datetime.isoformat()

    except Exception as e:
        print(f"Failed to combine time header and timestamp. Error: {e}")
        return None


def truncate_microseconds(dt):
    """Truncate microseconds from a datetime object."""
    return dt.replace(microsecond=0)


def reclassify_all_conversations(api_key):
    """
    Fetch all conversations from the database, reclassify them, and update their labels.
    """
    from .classify import classify_messages
    try:
        conversations = list(Conversation.objects.all().values(
            "thread_url", "username", "profile_url", "messages", "last_message_timestamp"
        ))

        if conversations:
            classified_conversations = classify_messages(
                conversations, api_key)
    except Exception as e:
        print(f"Failed to reclassify conversations. Error: {e}")
