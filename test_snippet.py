from modules.safetybench.test_runner import BenchmarkRunner
# If vLLM is not available, mock it
print("Module imports successfully")
# Check dataset loading
runner = BenchmarkRunner("test", "test")
data = runner.load_dataset()
print("Dataset loaded:", len(data), "items")
