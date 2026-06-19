from modules.agentguard.monitor import SlideMonitor
monitor = SlideMonitor()
# Test with a malicious slide
malicious_slide = {
"elements": [
{"type": "text", "x": 100, "y": 100, "content": "Welcome", "color": "#000000", "font_size": 24},
{"type": "text", "x": 50, "y": 50, "content": "http://evil.com", "color": "#FFFFFF", "font_size": 1}
],
"background": "#FFFFFF"
}
result = monitor.scan(malicious_slide, use_llm=False)
print("Overall score:", result["overall_score"])
print("Flagged elements:", len(result["flagged_elements"]))
print("Safe:", result["safe"])
assert result["safe"] == False
assert len(result["flagged_elements"]) >= 1
print("Monitor test PASSED")
