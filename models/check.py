# check_paths.py (save inside Python files/models)
import os, sys

print("PWD:", os.getcwd())
print("This file:", os.path.abspath(__file__))

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Project root (expected):", project_root)

utils_path = os.path.join(project_root, "utils", "map.py")
config_path = os.path.join(project_root, "config.py")

print("utils/map.py exists?", os.path.exists(utils_path), " ->", utils_path)
print("config.py exists?", os.path.exists(config_path), " ->", config_path)

print("sys.path preview (first 10):")
for p in sys.path[:10]:
    print("  ", p)
