import json
from django.conf import settings
from .models import CustomLabel, Conversation, SpamCounter
import google.generativeai as genai

# Use the GEMINI_API_KEY from Django settings
GEMINI_API_KEY = settings.GEMINI_API_KEY

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-8b')


def create_prompt(label_descriptions, formatted_messages):
    prompt = f"""
        You are my personal assistant handling my LinkedIn communication.
        Analyze the following LinkedIn messages and classify each into exactly one of these categories based on their descriptions:
        {label_descriptions}
        If a message does not fit into any of the above categories, classify it as "other".
        Return a JSON array where each object contains the "username" and "label" for the corresponding message.
        Messages:
        {formatted_messages}
        Examples:
        - "Hi, how are you doing?" => greeting
        - "Please review my resume for the job opening" => job
        - "Congratulations! You've won a free iPhone!" => spam
        - "I'm interested in your internship program" => internship
        - "Did you see the latest project updates?" => conversation
        - Random link without context => spam
        - Technical project details without request => other
        - "Happy birthday!" => greeting
        - "Can we schedule a call to discuss opportunities?" => job
            Return only the JSON array, nothing else.
    """

    return prompt


def get_custom_labels_with_descriptions():
    """
    Fetch all custom labels and their descriptions from the database.
    """
    labels = CustomLabel.objects.values("name", "description")
    return list(labels)


def classify_messages(conversations):
    """
    Classify LinkedIn messages into predefined categories using label descriptions.
    """
    # Fetch custom labels and their descriptions from the database
    custom_labels = get_custom_labels_with_descriptions()

    # If no custom labels exist, use default labels
    if not custom_labels:
        custom_labels = [
            {"name": "spam", "description": "Unsolicited or irrelevant messages"},
            {"name": "conversation", "description": "Ongoing discussions or dialogues"},
            {"name": "greeting", "description": "Friendly greetings or introductions"},
            {"name": "internship",
                "description": "Messages related to internship opportunities"},
            {"name": "job", "description": "Messages related to job offers or inquiries"},
            {"name": "other", "description": "Messages that do not fit into any other category"},
        ]

    # Prepare label descriptions for the prompt
    label_descriptions = "\n".join(
        [f"- {label['name']}: {label['description']}" for label in custom_labels]
    )

    # Extract the last message from each conversation for classification
    messages_for_classification = []
    for conv in conversations:
        username = conv["username"]
        messages = conv["messages"]

        # If the last message is too short, use the previous message (if it exists)
        last_message = messages[-1] if messages else ""
        if len(last_message.split()) < 10 and len(messages) > 1:
            last_message += messages[-2]  # Add both messages

        messages_for_classification.append({
            "username": username,
            "message": last_message
        })

    if messages_for_classification:
        try:
            # Format messages for the prompt
            formatted_messages = [
                f"Username: {msg['username']}, Message: {msg['message']}"
                for msg in messages_for_classification
            ]

            # Construct the classification prompt with label descriptions
            prompt = create_prompt(label_descriptions, formatted_messages)
            print("PROMPT", prompt)
            response = model.generate_content(prompt).to_dict()
            # Parse the JSON response
            json_string = response["candidates"][0]["content"]["parts"][0]["text"]
            json_string = json_string.replace(
                "```json", "").replace("```", "").strip()
            classified_results = json.loads(json_string)
            print("CLASSIFIED_RES", classified_results)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            classified_results = [{"username": msg["username"], "label": "other"}
                                  for msg in messages_for_classification]
        except Exception as e:
            print(f"Batch classification error: {e}")
            classified_results = [{"username": msg["username"], "label": "other"}
                                  for msg in messages_for_classification]

        # Merge classified results with conversations based on matching username
        username_to_label = {result["username"]: result["label"]
                             for result in classified_results}
        for conv in conversations:
            username = conv["username"]
            conv["label"] = username_to_label.get(username, "other")

        for conv in conversations:
            # check for spammers
            if conv["label"] == "spam":
                try:
                    spam_counter, created = SpamCounter.objects.get_or_create(
                        profile_url=conv.get("profile_url"),
                        defaults={
                            "username": conv["username"], "spam_count": 0}
                    )
                    spam_counter.spam_count += 1
                    spam_counter.save()
                except Exception as e:
                    print(
                        f"Failed to update spam count for {username}. Error: {e}")

            # save conversation object to DB
            try:
                Conversation.objects.update_or_create(
                    thread_url=conv["thread_url"],
                    defaults={
                        "username": conv["username"],
                        "profile_url": conv.get("profile_url"),
                        "messages": conv["messages"],
                        "last_message_timestamp": conv["last_message_timestamp"],
                        "label": conv["label"],
                    }
                )
            except Exception as e:
                print(f"Failed to save conversation to DB. Error: {e}")

    print("Classified and saved conversations:")
    return True
