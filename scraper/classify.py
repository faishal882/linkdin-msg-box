import json
from django.conf import settings

import google.generativeai as genai

# Use the GEMINI_API_KEY from Django settings
GEMINI_API_KEY = settings.GEMINI_API_KEY

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-8b')

# Classification labels
LABELS = ["spam", "conversation", "greeting", "internship", "job", "other"]

# Optimized classification prompt for batch processing
BATCH_CLASSIFICATION_PROMPT = """you are my personal assistant handling my LinkedIn communication.

Analyze the following LinkedIn messages and classify each into exactly one of these categories: {labels}.
Return a JSON array where each object contains the "username" and "label" for the corresponding message.

Messages:
{messages}

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


def classify_messages(conversations):
    """
    Classify LinkedIn messages into predefined categories.

    Args:
        conversations (list): List of conversation dictionaries with 'username' and 'messages'.

    Returns:
        list: List of conversations with an added 'label' key for each conversation.
    """
    # Extract the last message from each conversation for classification
    messages_for_classification = [
        {
            "username": conv["username"],
            "message": conv["messages"][-1] if conv["messages"] else ""
        }
        for conv in conversations
    ]

    if messages_for_classification:
        try:
            # Format messages for the prompt
            formatted_messages = [
                f"Username: {msg['username']}, Message: {msg['message']}"
                for msg in messages_for_classification
            ]
            prompt = BATCH_CLASSIFICATION_PROMPT.format(
                labels=", ".join(LABELS),
                messages="\n".join(formatted_messages)
            )

            response = model.generate_content(prompt).to_dict()

            # Parse the JSON response
            json_string = response["candidates"][0]["content"]["parts"][0]["text"]
            json_string = json_string.replace(
                "```json", "").replace("```", "").strip()
            classified_results = json.loads(json_string)
            print("Extracted JSON response:", classified_results)

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

    print("classified: ", conversations)

    return conversations
