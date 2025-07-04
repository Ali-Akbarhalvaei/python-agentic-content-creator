# src/news_fetcher/news_api.py
# Final Version: With optional date filtering for trending topics.

import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from the .env file.
load_dotenv(override=True)

# The base URL for the NewsAPI 'everything' endpoint.
NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"


def fetch_headlines(
    topics: List[str], date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetches news articles from NewsAPI based on topics, with an optional date filter.

    Args:
        topics (List[str]): A list of keywords to search for.
        date (Optional[str]): An optional date string in 'YYYY-MM-DD' format.
                              If provided, it searches for the most popular articles on that day.

    Returns:
        List[Dict[str, Any]]: A list of article dictionaries, or an empty list if it fails.
    """
    if not topics:
        print("Error: No topics provided to search for.")
        return []

    print(f"Attempting to fetch news for topics: {topics}...")
    if date:
        print(f"  - Filtering for date: {date}")

    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("Error: NEWS_API_KEY not found in your .env file.")
        return []

    query_string = " OR ".join(topics)

    # Start with base parameters
    params = {"q": query_string, "language": "en", "pageSize": 10, "apiKey": api_key}

    # Add optional parameters if a date is provided
    if date:
        params["from"] = date
        params["to"] = date
        params["sortBy"] = "popularity"  # Find the "hottest" topics for that day
    else:
        params["sortBy"] = "relevancy"  # Default behavior

    try:
        response = requests.get(NEWS_API_BASE_URL, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while calling NewsAPI: {e}")
        return []

    data = response.json()
    articles = data.get("articles", [])

    if not articles:
        print("No articles found for the specified criteria.")
        return []

    return articles


if __name__ == "__main__":
    print("--- Running News Fetcher Test ---")

    target_topics = ["finance", "politics"]

    print("\n--- Testing without date filter (default behavior) ---")
    recent_articles = fetch_headlines(topics=target_topics)
    if recent_articles:
        print(f"\nSuccessfully fetched {len(recent_articles)} recent articles:")
        for i, article in enumerate(recent_articles[:3], 1):  # Show first 3
            print(f"  {i}. {article.get('title')}")
    else:
        print("\nTest failed for recent articles.")

    print("\n\n--- Testing with today's date filter ---")
    today_str = datetime.now().strftime("%Y-%m-%d")
    todays_articles = fetch_headlines(topics=target_topics, date=today_str)

    if todays_articles:
        print(
            f"\nSuccessfully fetched {len(todays_articles)} of today's popular articles:"
        )
        for i, article in enumerate(todays_articles[:3], 1):  # Show first 3
            print(f"  {i}. {article.get('title')}")
    else:
        print(f"\nNo popular articles found for today, or test failed.")

    print("\n--- Test Complete ---")
