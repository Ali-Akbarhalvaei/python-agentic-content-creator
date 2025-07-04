# python-agentic-content-creator
An AI-powered content creation assistant for Instagram that automates research, copywriting, and image generation, controlled via a Telegram bot.



## The Problem

Content creation for social media is incredibly time-consuming, requiring constant research, copywriting, and visual design. A single high-quality post can take hours to produce, making consistency a major challenge for creators.

## The Solution

InstAgent solves this problem by acting as an autonomous creative assistant. It transforms the multi-hour process of creating a post into a single command, delivering a complete, "ready-to-post" content package in minutes.

## Core Features

* **Interactive Bot Interface:** Users interact with the agent through a user-friendly Telegram bot.
* **Flexible Topic Generation:** Generate content on any topic by sending a command like `/generate finance politics` or get the day's trending news with `/generate --date today`.
* **Automated Research:** Connects to the NewsAPI to fetch the latest, most relevant articles based on user-defined topics.
* **AI-Powered Strategy:** Uses the Google Gemini LLM to analyze articles and generate a complete content strategy, including captions, hashtags, and visual concepts.
* **Unique Image Creation:** Leverages the Google Imagen API to generate high-quality, symbolic, and copyright-free images for each post.
* **Branded Visuals:** Programmatically creates a consistent, branded headline slide and adds clean text overlays to all subsequent images.
* **Complete Content Packages:** The final output is delivered directly to the user's Telegram chat and saved locally in a neatly organized, timestamped folder.


## Sample Output

<table>
  <tr>
    <td><img src="output_2025-06-30_12-57-50/post_10_slide_01.png" alt="Branded Headline Slide" width="400"/></td>
    <td><img src="output_2025-06-30_12-57-50/post_10_slide_02.png" alt="Symbolic Image Slide1" width="400"/></td>
  </tr>
</table>

<table>
  <tr>
    <td><img src="output_2025-06-30_12-57-50/post_10_slide_03.png" alt="slide 2" width="400"/></td>
    <td><img src="output_2025-06-30_12-57-50/post_10_slide_04.png" alt=" Slide 3" width="400"/></td>
  </tr>
</table>


## System Architecture

InstAgent is built with a modular, layered architecture. A central **Orchestrator** (`main.py`) directs a team of specialist modules, each responsible for a single task. This design makes the system robust, scalable, and easy to maintain.


1.  **User Interface (`app.py`):** A Flask web server listens for commands from the Telegram bot.
2.  **Orchestrator (`main.py`):** Manages the end-to-end workflow.
3.  **Data Engine (`news_fetcher`):** Fetches news articles.
4.  **Creative Brain (`content_creation`):** Generates the content strategy (captions, prompts).
5.  **Visuals Module (`image_generator`):** Creates background images.
6.  **Image Compositor (`image_compositor`):** Creates the final slides with text overlays.

## Technology Stack

* **Language:** Python 3.9+
* **APIs & Services:**
    * Telegram Bot API
    * NewsAPI.org
    * Google Gemini API
    * Google Imagen API (via Vertex AI)
* **Core Libraries:**
    * `Flask` (Web Server)
    * `python-telegram-bot`
    * `requests`
    * `google-generativeai` & `google-cloud-aiplatform`
    * `Pillow` (Image Manipulation)
    * `python-dotenv` (Environment Variables)
    * `tenacity` (API Resilience)

## Setup & Usage

### 1. Prerequisites

* Python 3.9+
* A Telegram account
* API keys for NewsAPI, Google Cloud (Gemini/Imagen), and a Telegram Bot Token.
* Google Cloud CLI installed and authenticated (`gcloud auth application-default login`).

### 2. Installation

Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/your-username/InstAgent.git](https://github.com/your-username/InstAgent.git)
cd InstAgent
pip install -r requirements.txt
```

### 3. Configuration

1.  Create a `.env` file in the root directory.
2.  Add your API keys and Google Cloud Project ID to the `.env` file:
    ```
    TELEGRAM_BOT_TOKEN="your_token"
    NEWS_API_KEY="your_key"
    GOOGLE_API_KEY="your_key"
    GCP_PROJECT_ID="your-gcp-project-id"
    ```
3.  Create a `fonts` folder in the root directory and add the `Inter-Bold.ttf`, `Inter-Regular.ttf`, and `PlayfairDisplay-ExtraBold.ttf` font files.

### 4. Running the Agent

1.  **Start the Server:** In your terminal, run the Flask application.
    ```bash
    python app.py
    ```
2.  **Expose Your Server (if running locally):** In a second terminal, use `ngrok` to create a public URL for your server.
    ```bash
    ngrok http 4040
    ```
3.  **Set the Webhook:** Use the `ngrok` URL to set your bot's webhook with the Telegram API (this only needs to be done once per ngrok session).
4.  **Interact with the Bot:** Open Telegram and send commands to your bot!
    * `/generate finance`
    * `/generate AI technology --date today`

