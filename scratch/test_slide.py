import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.agentguard.environment import SlideEnvironment

def main():
    print("Testing SlideEnvironment...")
    slide = SlideEnvironment(width=1200, height=800, background="#ffffff")
    
    # Add title, subtitle, and body text
    slide.add_text(100, 50, "Welcome to Global South AI Safety Challenge", font_size=36, color="#000000")
    slide.add_text(100, 100, "Secure monitoring and control platform demo", font_size=24, color="#555555")
    slide.add_text(100, 150, "This is some body text element that should render beautifully.", font_size=20, color="#222222")
    
    # Add an image placeholder
    slide.add_image(300, 200, "nonexistent.png", width=100, height=100)
    
    # Add hidden text (white on white)
    slide.add_text(10, 10, "malicious_payload_x89", font_size=1, color="#fefefe")
    
    # Render normal
    img_normal = slide.render(reveal=False)
    img_normal.save("scratch/slide_normal.png")
    print("Saved normal slide to scratch/slide_normal.png")
    
    # Render reveal
    img_reveal = slide.render(reveal=True)
    img_reveal.save("scratch/slide_reveal.png")
    print("Saved reveal slide to scratch/slide_reveal.png")

if __name__ == "__main__":
    main()
