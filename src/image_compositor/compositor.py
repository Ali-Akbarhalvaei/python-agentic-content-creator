# src/image_compositor/compositor.py
# Final Version: Aligned with the final strategist output.

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from typing import List


def _find_font_file(font_names: List[str]) -> str:
    """
    Searches for a font file in the project's root 'fonts' directory.
    """
    project_font_dir = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
    for font_name in font_names:
        font_path = os.path.join(project_font_dir, font_name)
        if os.path.exists(font_path):
            print(f"Font found: '{font_path}'")
            return font_path
    print(
        f"Warning: Could not find any of the following fonts in the 'fonts' folder: {font_names}"
    )
    return None


def create_branded_headline_slide(headline_text: str, output_path: str) -> bool:
    """
    Creates our branded, text-only headline slide from scratch.
    """
    try:
        width, height = 1024, 1024
        background_color = "#F8F9FA"
        news_tag_bg = "#D92D20"
        news_tag_text = "LATEST NEWS"
        footer_text = "Finance & Politics Brief"

        main_font_path = _find_font_file(["PlayfairDisplay-ExtraBold.ttf"])
        tag_font_path = _find_font_file(["Inter-Bold.ttf"])

        if not main_font_path or not tag_font_path:
            print("❌ Error: Headline or Tag font not found in 'fonts' directory.")
            return False

        main_font = ImageFont.truetype(main_font_path, 80)
        tag_font = ImageFont.truetype(tag_font_path, 24)
        footer_font = ImageFont.truetype(tag_font_path, 20)

        img = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(img)

        margin = int(width * 0.1)
        draw.rectangle((margin, margin, margin + 180, margin + 40), fill=news_tag_bg)
        draw.text(
            (margin + 90, margin + 20),
            news_tag_text,
            font=tag_font,
            fill="white",
            anchor="mm",
        )

        avg_char_width = draw.textlength("A", font=main_font)
        wrap_at_char_count = (
            int((width - 2 * margin) / avg_char_width) if avg_char_width > 0 else 20
        )
        wrapped_text = "\n".join(textwrap.wrap(headline_text, width=wrap_at_char_count))

        text_bbox = draw.multiline_textbbox(
            (margin, 0), wrapped_text, font=main_font, align="left"
        )
        text_height = text_bbox[3] - text_bbox[1]
        text_y = (height - text_height) / 2
        draw.text(
            (margin, text_y), wrapped_text, font=main_font, fill="black", align="left"
        )

        draw.text(
            (width - margin, height - margin),
            footer_text,
            font=footer_font,
            fill="#6C757D",
            anchor="rs",
        )

        img.save(output_path)
        print(f"✅ Branded headline slide saved to '{output_path}'")
        return True

    except Exception as e:
        print(f"❌ An unexpected error occurred while creating branded slide: {e}")
        return False


# --- UPDATED FUNCTION SIGNATURE ---
def add_text_to_image(
    image_path: str, slide_title: str, slide_text: str, output_path: str
) -> bool:
    """
    Opens an image, draws a title and a short explanation on it, and saves the result.
    """
    try:
        with Image.open(image_path).convert("RGBA") as img:
            txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)

            title_font_path = _find_font_file(["Inter-Bold.ttf"])
            explanation_font_path = _find_font_file(["Inter-Regular.ttf"])

            if not title_font_path or not explanation_font_path:
                print(
                    "❌ Error: Inter-Bold.ttf or Inter-Regular.ttf not found in 'fonts' directory."
                )
                return False

            title_font = ImageFont.truetype(title_font_path, 80)
            explanation_font = ImageFont.truetype(explanation_font_path, 45)

            img_width, _ = img.size
            margin = int(img_width * 0.08)
            max_text_width_pixels = img_width - (2 * margin)

            avg_char_width_title = draw.textlength("a", font=title_font)
            wrap_title_at = (
                int(max_text_width_pixels / avg_char_width_title)
                if avg_char_width_title > 0
                else 30
            )
            wrapped_title = textwrap.wrap(slide_title, width=wrap_title_at)

            avg_char_width_exp = draw.textlength("a", font=explanation_font)
            wrap_exp_at = (
                int(max_text_width_pixels / avg_char_width_exp)
                if avg_char_width_exp > 0
                else 50
            )
            wrapped_explanation = textwrap.wrap(slide_text, width=wrap_exp_at)

            title_spacing = int(80 * 0.2)
            exp_spacing = int(45 * 0.2)
            space_between_blocks = 60

            total_height = -title_spacing
            for line in wrapped_title:
                bbox = draw.textbbox((0, 0), line, font=title_font)
                total_height += (bbox[3] - bbox[1]) + title_spacing
            total_height += space_between_blocks
            for line in wrapped_explanation:
                bbox = draw.textbbox((0, 0), line, font=explanation_font)
                total_height += (bbox[3] - bbox[1]) + exp_spacing

            max_line_width = (
                max(
                    [draw.textlength(line, font=title_font) for line in wrapped_title]
                    + [
                        draw.textlength(line, font=explanation_font)
                        for line in wrapped_explanation
                    ]
                )
                if (wrapped_title or wrapped_explanation)
                else 0
            )

            padding = 30
            bg_bbox = (
                margin - padding,
                margin - padding,
                margin + max_line_width + padding,
                margin + total_height + padding,
            )
            draw.rectangle(bg_bbox, fill=(0, 0, 0, 153))

            current_y = margin
            for line in wrapped_title:
                draw.text(
                    (margin, current_y),
                    line,
                    font=title_font,
                    fill="white",
                    align="left",
                )
                bbox = draw.textbbox((0, 0), line, font=title_font)
                current_y += (bbox[3] - bbox[1]) + title_spacing

            current_y += space_between_blocks

            for line in wrapped_explanation:
                draw.text(
                    (margin, current_y),
                    line,
                    font=explanation_font,
                    fill="white",
                    align="left",
                )
                bbox = draw.textbbox((0, 0), line, font=explanation_font)
                current_y += (bbox[3] - bbox[1]) + exp_spacing

            out = Image.alpha_composite(img, txt_layer)
            out.convert("RGB").save(output_path)
            print(f"✅ Image with title and explanation saved to '{output_path}'")
            return True

    except Exception as e:
        print(f"❌ An unexpected error occurred in the compositor: {e}")
        return False


if __name__ == "__main__":
    print("--- Running Image Compositor Test ---")

    print("\n--- Testing Branded Headline Slide ---")
    headline = "Central Bank Signals Potential Interest Rate Hike Next Quarter."
    create_branded_headline_slide(headline, "test_headline_slide.png")

    print("\n--- Testing Text on Image Slide ---")
    if not os.path.exists("test_image_google.png"):
        Image.new("RGB", (1024, 1024), color="gray").save("test_image_google.png")

    background_image = "test_image_google.png"
    sample_title = "The Market Reacts"
    sample_explanation = (
        "Investors are cautiously optimistic following the Fed's announcement."
    )
    output_image = "test_image_with_text.png"

    add_text_to_image(
        image_path=background_image,
        slide_title=sample_title,  # Using the new parameter names
        slide_text=sample_explanation,  # Using the new parameter names
        output_path=output_image,
    )
