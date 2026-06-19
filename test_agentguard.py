from modules.agentguard.environment import SlideEnvironment
slide = SlideEnvironment()
slide.add_text(100, 100, "Hello", "#000000", 24)
slide.add_text(100, 200, "Hidden", "#FFFFFF", 12) # white on white
slide.set_background("#FFFFFF")
img = slide.render()
print("Image size:", img.size)
print("JSON:", slide.export_json())
