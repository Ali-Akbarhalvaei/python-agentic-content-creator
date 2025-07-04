# src/content_creation/strategist.py
# Final Version: Implemented the "Branded Headline Slide" strategy.

import os
import json
import requests
import google.generativeai as genai
from typing import Dict, Union
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from google.api_core import exceptions as google_exceptions

# Load environment variables.
load_dotenv(override=True)

# Configure the Google AI client
try:
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")

    genai.configure(api_key=google_api_key)

    model = genai.GenerativeModel("gemini-1.5-flash-latest")

except Exception as e:
    print(f"Error configuring Google AI client: {e}")
    model = None

# --- FINALIZED, ADVANCED PROMPT TEMPLATE ---
PROMPT_TEMPLATE = """
You are an expert social media strategist for an Instagram page that explains complex politics and finance in a simple and visually engaging way. Your brand identity is clean, modern, and authoritative.

Your task is to take a serious news article and transform it into a complete Instagram Carousel post.

**News Headline:**
"{headline}"

**Full Article Content:**
"{article_content}"

**Your Instructions:**
1.  **Headline Slide:** First, create the text for a "Branded Headline Slide". This should be a very short, powerful headline (MAX 15 words) that grabs attention immediately. This will be the first slide.
2.  **Symbolic Slides:** Next, create a script for 2-3 additional slides that visually explain the story. For EACH of these slides, you MUST provide:
    * `slide_title`: A very short, punchy title (MAX 5 WORDS). This is the text that will be written on the image in Bold font.
    * `slide_text`: A short, explanation about the title (MAX 40 WORDS). This is the text that will be written on the image in Normal font.
    * `image_prompt`: A detailed description for a symbolic background image for that slide.
3.  **Write the Final Post Caption:**
    * Start with a hook.
    * Write a coherent, easy-to-read narrative for the caption.
    * End with a call-to-action and relevant hashtags.
4.  **!!! IMPORTANT SAFETY RULE !!!** For all `image_prompt` descriptions, you must **never** include the names of public figures (especially politicians) or ask for images of real people. You must also avoid describing people showing strong negative emotions like anger. Instead, you must describe a **symbolic or metaphorical image** that represents the concept. For example, instead of 'Two politicians arguing,' describe 'A red and a blue chess piece on opposite sides of a chessboard.' This is a critical safety requirement.

**Output Format:**
Return your complete analysis ONLY in a valid JSON format with the following strict structure:
- "headline_slide_text": (string) The text for the first, branded slide.
- "symbolic_slides": An array of objects. Each object MUST have "slide_title" (string), "slide_text" (string), and "image_prompt" (string) keys.
- "post_caption": (string) The final, detailed caption.
- "hashtags": (an array of strings)
"""


def _scrape_article_content(url: str) -> str:
    """A helper function to scrape the main text content from a news article URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join([p.get_text() for p in paragraphs])
    except Exception as e:
        print(f"Warning: Could not scrape article content from {url}. Reason: {e}")
        return ""


@retry(
    retry=retry_if_exception_type(google_exceptions.ResourceExhausted),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    stop=stop_after_attempt(5),
)
def generate_content_strategy(article: Dict) -> Union[Dict, None]:
    if not model:
        print("Google AI Model is not initialized. Cannot generate strategy.")
        return None

    headline = article.get("title", "No Title")
    url = article.get("url", "")

    print(f"\nGenerating content strategy for article: '{headline}'...")

    article_content = _scrape_article_content(url)
    if not article_content:
        print("Falling back to using only the headline due to scraping failure.")
        article_content = headline

    prompt = PROMPT_TEMPLATE.format(headline=headline, article_content=article_content)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            ),
        )
        content = response.text
        result = json.loads(content)
        return result
    except Exception as e:
        print(f"An unexpected error occurred during API call: {e}")
        return None


if __name__ == "__main__":
    print("--- Running Content Strategist Test ---")

    try:
        with open("test_headlines.json", "r", encoding="utf-8") as f:
            test_articles = json.load(f)
        article_to_test = test_articles[0]
    except (FileNotFoundError, IndexError):
        article_to_test = {
            "title": "Federal Reserve signals potential rate hikes.",
            "url": "",
        }

    strategy = generate_content_strategy(article_to_test)

    if strategy:
        print("\n✅ Strategy generation successful!")
        print(json.dumps(strategy, indent=2))
    else:
        print("\n❌ Strategy generation failed.")

    print("\n--- Test Complete ---")
