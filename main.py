# main.py
# Final Version: With flexible arguments for topics and date, controlled by the app or command line.

import os
import json
from datetime import datetime
import shutil
from typing import Optional, List
import sys  # Import sys to read command-line arguments

# --- Import all our final, specialized functions ---
from src.news_fetcher.news_api import fetch_headlines
from src.content_creation.strategist import generate_content_strategy
from src.image_generator.imagen_api import create_image
from src.image_compositor.compositor import (
    add_text_to_image,
    create_branded_headline_slide,
)


def create_output_folder() -> str:
    """Creates a new, timestamped folder for the output files."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"output_{timestamp}"
    os.makedirs(folder_name, exist_ok=True)
    print(f"✅ Created output folder: '{folder_name}'")
    return folder_name


def save_caption(folder: str, post_number: int, strategy: dict):
    """Saves the final caption and hashtags to a text file."""
    caption_filename = os.path.join(folder, f"post_{post_number:02d}_caption.txt")
    try:
        with open(caption_filename, "w", encoding="utf-8") as f:
            f.write("--- POST CAPTION ---\n\n")
            f.write(strategy.get("post_caption", "No caption generated."))
            f.write("\n\n--- HASHTAGS ---\n\n")
            hashtags = " ".join(strategy.get("hashtags", []))
            f.write(hashtags)
        print(f"  - ✅ Caption saved to '{caption_filename}'")
    except IOError as e:
        print(f"  - ❌ Error saving caption: {e}")


# The workflow now accepts a list of topics and an optional date filter
def run_workflow(topics: List[str], date_filter: Optional[str] = None) -> Optional[str]:
    """
    The main workflow. Returns the path to the output folder on success, otherwise None.
    """
    print(f"🚀 Starting AI Creative Assistant Workflow for topics: {topics}...")

    # --- Step 1: Fetch Niche-Specific Headlines ---
    articles = fetch_headlines(topics=topics, date=date_filter)
    if not articles:
        print("Workflow failed: Could not fetch articles.")
        return None  # Return None on failure

    output_folder = create_output_folder()

    for i, article in enumerate(articles):
        post_num = i + 1
        print(f"\n--- Processing Post {post_num}/{len(articles)} ---")

        if not isinstance(article, dict):
            print(f"  - ⚠️ Warning: Skipping malformed article data.")
            continue

        # --- Step 2: Generate Content Strategy ---
        print(
            f"[2/4] Generating content strategy for: '{article.get('title', 'Untitled')[:40]}...'"
        )
        strategy = generate_content_strategy(article)
        if not strategy:
            print("  - ❌ Skipping article due to strategy generation failure.")
            continue

        print("  - ✅ Strategy generated successfully.")
        print(f"[3/4] Generating visual assets...")

        # --- Step 3: Generate Visuals ---
        headline_text = strategy.get("headline_slide_text")
        if headline_text:
            slide_path = os.path.join(
                output_folder, f"post_{post_num:02d}_slide_01.png"
            )
            create_branded_headline_slide(headline_text, slide_path)

        symbolic_slides = strategy.get("symbolic_slides", [])
        for slide_num, slide_content in enumerate(symbolic_slides):
            slide_index = slide_num + 2
            print(
                f"  - Processing Symbolic Slide {slide_index-1}/{len(symbolic_slides)}..."
            )

            image_prompt = slide_content.get("image_prompt")
            bg_image_path = os.path.join(
                output_folder, f"temp_bg_{post_num:02d}_{slide_index}.png"
            )

            if create_image(prompt=image_prompt, filename=bg_image_path):
                slide_title = slide_content.get("slide_title", "")
                slide_text = slide_content.get("slide_text", "")
                final_slide_path = os.path.join(
                    output_folder, f"post_{post_num:02d}_slide_{slide_index:02d}.png"
                )

                add_text_to_image(
                    image_path=bg_image_path,
                    slide_title=slide_title,
                    slide_text=slide_text,
                    output_path=final_slide_path,
                )
                os.remove(bg_image_path)
            else:
                print(
                    f"    - ❌ Failed to create background image for slide {slide_index}. Skipping."
                )

        # --- Step 4: Save the Final Caption ---
        print(f"[4/4] Saving final caption...")
        save_caption(output_folder, post_num, strategy)

    print(
        f"\n✅ Workflow Complete! Check the '{output_folder}' folder for your content packages."
    )
    return output_folder  # Return the folder path on success


if __name__ == "__main__":
    # This block allows us to run the orchestrator directly from the command line for testing.
    # Example usage:
    # python main.py finance politics
    # python main.py AI technology --date today

    # 1. Initialize default values
    topics = []
    date_arg = None

    # 2. Parse arguments from the command line
    args = sys.argv[1:]

    # 3. Check for the optional date flag
    if "--date" in args and "today" in args:
        date_arg = datetime.now().strftime("%Y-%m-%d")
        # Remove the flags so they aren't treated as topics
        args.remove("--date")
        args.remove("today")

    # 4. The remaining arguments are treated as topics
    topics = args

    # 5. If no topics were provided, use our default list
    if not topics:
        print(
            "No topics provided via command line. Using default topics: ['finance', 'politics']"
        )
        topics = ["finance", "politics"]

    # 6. Run the workflow with the parsed arguments
    run_workflow(topics=topics, date_filter=date_arg)
