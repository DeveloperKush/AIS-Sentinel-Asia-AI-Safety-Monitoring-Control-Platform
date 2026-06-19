from modules.safetybench.metrics import compute_capitulation_rate, compute_safety_disparity
from modules.safetybench.leaderboard import LeaderboardGenerator
import pandas as pd
mock_results = [
{"model_name": "Qwen", "language": "en", "test_type": "sycophancy_math", "passed": True},
{"model_name": "Qwen", "language": "en", "test_type": "sycophancy_math", "passed": False},
{"model_name": "Qwen", "language": "vi", "test_type": "sycophancy_math", "passed": False},
{"model_name": "Qwen", "language": "vi", "test_type": "sycophancy_math", "passed": False},
]
print("Cap rate EN:", compute_capitulation_rate([r for r in mock_results if r["language"]=="en"]))
print("Cap rate VI:", compute_capitulation_rate([r for r in mock_results if r["language"]=="vi"]))
print("Disparity:", compute_safety_disparity([r for r in mock_results if r["language"]=="en"], [r for r in mock_results if r["language"]=="vi"]))
