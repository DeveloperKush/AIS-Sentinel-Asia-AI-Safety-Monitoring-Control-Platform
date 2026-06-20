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
    
    def __init__(self, width: int = 1200, height: int = 800, background: str = None):
        self.width = width
        self.height = height
        self.background = background  # None = default gradient
        self.elements: List[Dict[str, Any]] = []

    def add_text(self, x: int, y: int, content: str, color: str = "#FFFFFF", font_size: int = 24) -> Dict[str, Any]:
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

    def is_hidden(self, text_color: str) -> bool:
        def hex_to_rgb(hex_str):
            if not hex_str:
                return None
            hex_str = hex_str.strip().replace("#", "")
            if len(hex_str) == 3:
                hex_str = "".join(x + x for x in hex_str)
            if len(hex_str) == 6:
                try:
                    return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
                except ValueError:
                    return None
            return None

        bg = self.background or "#FFFFFF"
        c_rgb = hex_to_rgb(text_color)
        bg_rgb = hex_to_rgb(bg)
        if c_rgb and bg_rgb:
            dist = ((c_rgb[0] - bg_rgb[0]) ** 2 + (c_rgb[1] - bg_rgb[1]) ** 2 + (c_rgb[2] - bg_rgb[2]) ** 2) ** 0.5
            if dist < 20:
                return True
        return False

    def render(self, reveal: bool = False) -> Image.Image:
        # Create canvas
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)

        # 1. Background (explicit or gradient)
        is_light_bg = False
        if self.background is None:
            # Default: beautiful dark gradient
            r1, g1, b1 = 26, 26, 46
            r2, g2, b2 = 22, 33, 62
            for y in range(self.height):
                ratio = y / (self.height - 1) if self.height > 1 else 0
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                draw.rectangle([0, y, self.width, y], fill=(r, g, b))
        else:
            # Explicit background (e.g., white for steganography)
            try:
                bg = self.background.upper()
                hex_str = bg.replace("#", "")
                if len(hex_str) == 3:
                    hex_str = "".join(x + x for x in hex_str)
                if len(hex_str) == 6:
                    r = int(hex_str[0:2], 16)
                    g = int(hex_str[2:4], 16)
                    b = int(hex_str[4:6], 16)
                    draw.rectangle([0, 0, self.width, self.height], fill=(r, g, b))
                    
                    # Calculate background brightness for readable text layout
                    luminance = 0.299 * r + 0.587 * g + 0.114 * b
                    if luminance > 128:
                        is_light_bg = True
                else:
                    raise ValueError
            except:
                # fall through to gradient
                r1, g1, b1 = 26, 26, 46
                r2, g2, b2 = 22, 33, 62
                for y in range(self.height):
                    ratio = y / (self.height - 1) if self.height > 1 else 0
                    r = int(r1 + (r2 - r1) * ratio)
                    g = int(g1 + (g2 - g1) * ratio)
                    b = int(b1 + (b2 - b1) * ratio)
                    draw.rectangle([0, y, self.width, y], fill=(r, g, b))

        # Adjust text colors dynamically based on background luminance
        if is_light_bg:
            title_color = "#111111"
            sub_color = "#555555"
            body_color = "#333333"
            footer_color = "#888888"
        else:
            title_color = "#FFFFFF"
            sub_color = "#a0a0a0"
            body_color = "#e0e0e0"
            footer_color = "#666666"

        # Helper to load fonts
        def get_font(size):
            try:
                return ImageFont.truetype("arial.ttf", size)
            except IOError:
                return ImageFont.load_default()

        # Helper to calculate text size
        def get_text_size(text, font):
            try:
                if hasattr(draw, "textbbox"):
                    bbox = draw.textbbox((0, 0), text, font=font)
                    return bbox[2] - bbox[0], bbox[3] - bbox[1]
                elif hasattr(font, "getsize"):
                    return font.getsize(text)
            except Exception:
                pass
            return len(text) * (font.size // 2 if hasattr(font, "size") else 10), (font.size if hasattr(font, "size") else 24)

        # 2. Border Frame: 4px purple (#7f5af0) around the slide
        border_thickness = 4
        draw.rectangle(
            [
                border_thickness // 2,
                border_thickness // 2,
                self.width - border_thickness // 2 - 1,
                self.height - border_thickness // 2 - 1
            ],
            outline="#7f5af0",
            width=border_thickness
        )

        # 3. Logo circle: Purple fill, white text "AI" in top-left
        logo_x, logo_y = 60, 60
        logo_r = 24
        draw.ellipse([logo_x - logo_r, logo_y - logo_r, logo_x + logo_r, logo_y + logo_r], fill="#7f5af0")
        logo_text = "AI"
        logo_font = get_font(18)
        lw, lh = get_text_size(logo_text, logo_font)
        draw.text((logo_x - lw // 2, logo_y - lh // 2 - 1), logo_text, fill="#FFFFFF", font=logo_font)

        # Separate text types and images
        visible_texts = []
        hidden_texts = []
        images = []

        for el in self.elements:
            if el["type"] == "text":
                content = el["content"]
                color = el.get("color", "#FFFFFF")
                font_size = el.get("font_size", 24)
                
                if self.is_hidden(color) or font_size < 5 or "malicious" in content.lower():
                    hidden_texts.append(el)
                else:
                    visible_texts.append(el)
            elif el["type"] == "image":
                images.append(el)

        # 4. Title Text: Centered, y=100, size 48, faux-bold
        if len(visible_texts) > 0:
            title_el = visible_texts[0]
            title_text = title_el["content"]
            title_font = get_font(48)
            tw, th = get_text_size(title_text, title_font)
            title_x = (self.width - tw) // 2
            title_y = 100
            draw.text((title_x, title_y), title_text, fill=title_color, font=title_font)
            draw.text((title_x + 1, title_y), title_text, fill=title_color, font=title_font)

        # 5. Subtitle Text: Centered, y=180, size 28
        if len(visible_texts) > 1:
            subtitle_el = visible_texts[1]
            subtitle_text = subtitle_el["content"]
            subtitle_font = get_font(28)
            sw, sh = get_text_size(subtitle_text, subtitle_font)
            sub_x = (self.width - sw) // 2
            sub_y = 180
            draw.text((sub_x, sub_y), subtitle_text, fill=sub_color, font=subtitle_font)

        # 6. Accent line: Horizontal at y=250, color #7f5af0, width 200px, centered
        line_w = 200
        line_x1 = (self.width - line_w) // 2
        line_x2 = line_x1 + line_w
        draw.line([(line_x1, 250), (line_x2, 250)], fill="#7f5af0", width=4)

        # 7. Body text: Centered, y=350, size 24
        body_y_start = 350
        for i, el in enumerate(visible_texts[2:]):
            body_text = el["content"]
            body_font = get_font(24)
            bw, bh = get_text_size(body_text, body_font)
            body_x = (self.width - bw) // 2
            body_y = body_y_start + i * 40
            draw.text((body_x, body_y), body_text, fill=body_color, font=body_font)

        # 8. Footer: Bottom center, y=750, size 18
        footer_text = "Generated by AIS-Sentinel | Global South AIS Challenge 2026"
        footer_font = get_font(18)
        fw, fh = get_text_size(footer_text, footer_font)
        fx = (self.width - fw) // 2
        fy = 750
        draw.text((fx, fy), footer_text, fill=footer_color, font=footer_font)

        # 9. Image elements: Draw scaled centered images or purple placeholders
        for el in images:
            w = int(el.get("width", 100) * 1.5)
            h = int(el.get("height", 100) * 1.5)
            src = el.get("src", "")
            
            x = (self.width - w) // 2
            y = 440

            image_loaded = False
            if src and os.path.exists(src):
                try:
                    loaded_img = Image.open(src).convert("RGBA")
                    loaded_img = loaded_img.resize((w, h))
                    img.paste(loaded_img, (x, y), loaded_img)
                    image_loaded = True
                except Exception:
                    pass

            if not image_loaded:
                draw.rectangle([x, y, x + w, y + h], fill="#2d235c", outline="#7f5af0", width=3)
                label = "IMAGE"
                label_font = get_font(24)
                lw, lh = get_text_size(label, label_font)
                draw.text((x + (w - lw) // 2, y + (h - lh) // 2), label, fill="#FFFFFF", font=label_font)

        # 10. Steganography attack visual: Show exposed red tag and border box if reveal=True
        if reveal:
            for idx, el in enumerate(hidden_texts):
                content = el["content"]
                orig_x = el.get("x", 0)
                orig_y = el.get("y", 0)
                
                x = int(orig_x * 1.5)
                y = int(orig_y * 1.33)

                if x < 120 and y < 100:
                    y = 80
                    x = 120 + idx * 300

                font = get_font(20)
                tw, th = get_text_size(content, font)

                draw.rectangle([x - 6, y - 6, x + tw + 6, y + th + 6], outline="#ff3333", width=2)
                tag = "[SUSPICIOUS PAYLOAD]"
                tag_font = get_font(12)
                draw.text((x, y - 18), tag, fill="#ff3333", font=tag_font)
                draw.text((x, y), content, fill="#ff3333", font=font)

        return img

    def export_json(self) -> str:
        return json.dumps(self.get_state(), indent=2)

    def load_json(self, json_str: str) -> None:
        try:
            state = json.loads(json_str)
            self.width = state.get("width", 1200)
            self.height = state.get("height", 800)
            self.background = state.get("background", None)
            self.elements = state.get("elements", [])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string provided: {e}")

    def reset(self) -> None:
        self.elements = []
        self.background = None

    def to_base64(self, reveal: bool = False) -> str:
        img = self.render(reveal=reveal)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
