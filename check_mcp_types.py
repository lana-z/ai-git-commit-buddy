import inspect
from mcp import types

# Print all available classes and functions in mcp.types
print("Available in mcp.types:")
for name, obj in inspect.getmembers(types):
    if not name.startswith("_"):  # Skip private/internal items
        print(f"- {name}: {type(obj)}")
