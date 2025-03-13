import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


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


def scrape_conversations(driver):
    """Scrape all conversations and return a list of conversations."""
    conversations = []
    try:
        # Find all conversation elements
        conversation_elements = driver.find_elements(
            # Limit to 10 conversations
            By.CSS_SELECTOR, ".msg-conversation-listitem")[:10]
        for index, element in enumerate(conversation_elements):
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

        # extracts messages
        messages = []
        message_elements = soup.select(".msg-s-event-listitem__body")
        for msg_element in message_elements:
            message = msg_element.text.strip()
            messages.append(message)

        return {
            "username": username,
            "thread_url": thread_url,
            "messages": messages,
        }
    except Exception as e:
        print(f"Failed to extract conversation details. Error: {e}")
        return None
