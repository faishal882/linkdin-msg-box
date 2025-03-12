import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

# Initialize the WebDriver (make sure you have the appropriate driver installed, e.g., chromedriver)
driver = webdriver.Chrome()

# Load the HTML file into the browser (replace 'path_to_file' with the actual path to your HTML file)
driver.get("./scapped_pages/conversation_1.html")

# Wait for the page to load completely (you might need to adjust the sleep time or use explicit waits)
time.sleep(3)

# Locate all chat elements (update the selector based on the actual HTML structure)
chat_elements = driver.find_elements(
    By.CSS_SELECTOR, "div.chat-item")  # Example selector

# Initialize a list to store the extracted data
chats_data = []

# Loop through each chat element and extract the username and profile photo link
for chat in chat_elements:
    try:
        # Extract username (update the selector based on the actual HTML structure)
        username_element = chat.find_element(By.CSS_SELECTOR, "span.username")
        username = username_element.text.strip()

        # Extract profile photo link (update the selector based on the actual HTML structure)
        profile_photo_element = chat.find_element(
            By.CSS_SELECTOR, "img.profile-photo")
        profile_photo_link = profile_photo_element.get_attribute("src")

        # Append the data to the list
        chats_data.append({
            "username": username,
            "profile_photo_link": profile_photo_link
        })
    except Exception as e:
        print(f"Error extracting data: {e}")

# Convert the data to JSON format
json_data = json.dumps(chats_data, indent=4)

# Print the JSON data
print(json_data)

# Save the JSON data to a file (optional)
with open("linkedin_chats.json", "w") as json_file:
    json_file.write(json_data)

# Close the WebDriver
driver.quit()
