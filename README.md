# LinkedIn Inbox (Backend)

## Overview

The LinkedIn Inbox Backend is a Python-based application designed to scrape LinkedIn messages, classify them into predefined categories using AI.

---

## Technologies Used

- **Python 3.12**: The core programming language used for development.
- **BeautifulSoup4**: For parsing HTML content scraped from LinkedIn.
- **Django**: A high-level Python web framework used as the backend.
- **REST API**: APIs are built using Django REST Framework for communication between frontend and backend.
- **Gemini AI**: Utilized for classifying LinkedIn messages into categories like "spam," "conversation," "job," etc.
- **Selenium**: For browser automation to interact with LinkedIn's web interface.
- **SQLite3**: A lightweight database used for storing scraped and classified data.

---

## Features

1. **Scraping LinkedIn Messages**:

   - Uses Selenium to automate browser actions and extract conversation threads.
   - Parses HTML content using BeautifulSoup to retrieve message details.

2. **Message Classification**:

   - Leverages Gemini AI to classify messages into predefined categories such as "spam," "greeting," "job," etc.\

3. **Custom Label**:

   - For classifying messages based on custom label

4. **Database Storage**:

   - Stores scraped conversations and their classifications in SQLite3 for easy retrieval and analysis.

5. **RESTful API**:
   - Provides endpoints to trigger scraping, fetch conversations, and manage custom labels.

---

## How to Run

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-repo-linkedin-inbox.git
cd linkedin-inbox
```

### Step 2: Create and activate the virtual enviornment

```bash
#Ubuntu
python3 -m venv venv
source venv\Scripts\activate
```

### Step 3: Install the requirements

```bash
pip install -r requirements.txt
```

### Step 4: Set up the SQLite3 database by applying migrations:

```bash
python manage.py migrate
```

### Step 5: run the server:

```bash
python manage.py runserver
```

## Project directory structure

```bash
linkedin_scraper/
├── scraper/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── classify.py          # Message classification logic
│   ├── models.py            # Database models
│   ├── serializers.py       # Serializers for API responses
│   ├── urls.py              # API endpoints
│   ├── utils.py             # Utility functions (e.g., scraping)
│   └── views.py             # View functions for handling API requests
├── linkedin_scraper/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── db.sqlite3               # SQLite database file
├── manage.py                # Django management script
├── requirements.txt         # List of dependencies
└── README.md                # Project documentation
```
