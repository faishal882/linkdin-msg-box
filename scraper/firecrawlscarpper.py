import firecrawl
import json

# Replace with your actual FireCrawl API key
API_KEY = ''

# Example cookie JSON string received from frontend


def firecrawl_scrapper(request, cookies):
    cookie_list = []
    for cookie in cookies:
        if all(key in cookie for key in ["name", "value"]):
            try:
                cookie_list.append({
                    "name": cookie["name"],
                    "value": cookie["value"],
                })
            except Exception as e:
                print(
                    f"Failed to add cookie: {cookie['name']}. Error: {e}")
    else:
        print(f"Skipping invalid cookie: {cookie}")

    cookie_header = "; ".join(
        [f"{cookie['name']}={cookie['value']}" for cookie in cookies])

    # Initialize the FirecrawlApp with your API key
    app = firecrawl.FirecrawlApp(api_key=API_KEY)

    # Define headers including the 'Cookie' header
    headers = {
        'Cookie': cookie_header
    }

    # Define scrape options
    scrape_options = {
        'formats': ['markdown'],
        'headers': headers
    }

    # URL to scrape
    url = 'https://www.linkedin.com/messaging/'

    # Execute the scrape request
    scrape_response = app.scrape_url(url, params=scrape_options)

    # Handle the response
    if scrape_response.get('success'):
        print('Scrape successful!')
        print(scrape_response.get('data'))
    else:
        print('Scrape failed:', scrape_response.get('error'))
