# src/image_generator/imagen_api.py
# Day 5: Re-engineered to use Google's Imagen model via Vertex AI.

import os
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from dotenv import load_dotenv


# Load environment variables. We now need GOOGLE_API_KEY and GCP_PROJECT_ID.
load_dotenv(override=True)

# --- NEW: CONFIGURE VERTEX AI ---
# This is the official way to set up the connection to Google's AI Platform.
try:
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID not found in your .env file.")

    # You may need to specify a location, e.g., "us-central1"
    vertexai.init(project=project_id, location="us-central1")

    # Load the Imagen model
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    print("✅ Vertex AI and Imagen model configured successfully.")

except Exception as e:
    print(f"❌ Error configuring Vertex AI: {e}")
    print(
        "   - Please ensure you have enabled the 'Vertex AI API' in your Google Cloud project."
    )
    print("   - Make sure your GCP_PROJECT_ID is correct in the .env file.")
    model = None


def create_image(prompt: str, filename: str) -> bool:
    """
    Generates an image using Google's Imagen model and saves it to a file.

    Args:
        prompt (str): The detailed text description for the image.
        filename (str): The path to save the generated image file (e.g., "post_image.png").

    Returns:
        bool: True if the image was generated and saved successfully, False otherwise.
    """
    if not model:
        print("Imagen model not initialized. Cannot generate image.")
        return False

    print(f"\n🎨 Generating image with Google Imagen for prompt: '{prompt[:50]}...'")

    try:
        # 1. Call the Imagen API to generate the image.
        # This API can generate multiple images, but we only need one.
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            # You can add more parameters here for style, aspect ratio, etc.
        )

        # 2. The response contains the image data directly.
        # We save the first (and only) image from the list.
        response[0].save(location=filename, include_generation_parameters=False)

        print(f"✅ Image successfully generated and saved as '{filename}'")
        return True

    except Exception as e:
        print(f"❌ An error occurred during image generation: {e}")
        return False


if __name__ == "__main__":
    print("\n--- Running Image Generator Test (with Google Imagen) ---")

    # A safe, creative prompt for testing.
    test_prompt = "A vibrant oil painting of a futuristic, domed city on a distant alien planet, with two glowing moons in the purple sky."
    output_filename = "test_image_google.png"

    # Call the image generation function
    success = create_image(prompt=test_prompt, filename=output_filename)

    if success:
        print(
            "\nTest successful. Check your project folder for 'test_image_google.png'."
        )
    else:
        print("\nTest failed.")

    print("\n--- Test Complete ---")
