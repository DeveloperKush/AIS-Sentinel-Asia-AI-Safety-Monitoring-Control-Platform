import json
import base64
import os
from io import BytesIO
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

class SlideEnvironment:
    """
    Simulates a presentation slide designer.
    Provides methods to add text and images, set background,
    render to a PIL Image, and serialize/deserialize to JSON.
    """
    
    def __init__(self, width: int = 800, height: int = 600, background: str = "#FFFFFF"):
        self.width = width
        self.height = height
        self.background = background
        self.elements: List[Dict[str, Any]] = []

    def add_text(self, x: int, y: int, content: str, color: str = "#000000", font_size: int = 24) -> Dict[str, Any]:
        element = {
            "type": "text",
            "x": x,
            "y": y,
            "content": content,
            "color": color,
            "font_size": font_size
        }
        self.elements.append(element)
        return element

    def add_image(self, x: int, y: int, src: str, width: int = 100, height: int = 100) -> Dict[str, Any]:
        element = {
            "type": "image",
            "x": x,
            "y": y,
            "src": src,
            "width": width,
            "height": height
        }
        self.elements.append(element)
        return element

    def set_background(self, color: str) -> None:
        self.background = color

    def get_state(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "background": self.background,
            "elements": self.elements
        }

    def render(self) -> Image.Image:
        # Create a blank canvas with the specified background color
        img = Image.new("RGB", (self.width, self.height), color=self.background)
        draw = ImageDraw.Draw(img)

        for el in self.elements:
            if el["type"] == "text":
                x, y = el["x"], el["y"]
                content = el["content"]
                color = el.get("color", "#000000")
                font_size = el.get("font_size", 24)
                
                try:
                    # Attempt to load a common font for proper sizing
                    font = ImageFont.truetype("arial.ttf", font_size)
                except IOError:
                    # Fallback to default font if arial is not available on the system
                    font = ImageFont.load_default()
                
                draw.text((x, y), content, fill=color, font=font)

            elif el["type"] == "image":
                x, y = el["x"], el["y"]
                w, h = el.get("width", 100), el.get("height", 100)
                src = el.get("src", "")
                
                try:
                    # Try to load and paste the actual image if it exists
                    loaded_img = Image.open(src).convert("RGBA")
                    loaded_img = loaded_img.resize((w, h))
                    # Use the image itself as a mask to handle transparency
                    img.paste(loaded_img, (x, y), loaded_img)
                except Exception:
                    # Draw a placeholder rectangle if the image cannot be loaded
                    draw.rectangle([x, y, x + w, y + h], fill="#CCCCCC", outline="#000000")
                    
                    label = f"Image: {os.path.basename(src)}" if src else "Image Placeholder"
                    font = ImageFont.load_default()
                    
                    # Approximate centering for the label
                    bbox = draw.textbbox((0, 0), label, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                    
                    text_x = x + max(0, (w - text_w) // 2)
                    text_y = y + max(0, (h - text_h) // 2)
                    draw.text((text_x, text_y), label, fill="#000000", font=font)

        return img

    def export_json(self) -> str:
        return json.dumps(self.get_state(), indent=2)

    def load_json(self, json_str: str) -> None:
        try:
            state = json.loads(json_str)
            self.width = state.get("width", 800)
            self.height = state.get("height", 600)
            self.background = state.get("background", "#FFFFFF")
            self.elements = state.get("elements", [])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string provided: {e}")

    def reset(self) -> None:
        self.elements = []
        self.background = "#FFFFFF"

    def to_base64(self) -> str:
        img = self.render()
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
