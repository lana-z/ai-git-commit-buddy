import inspect
from mcp.server import Server

# Print all available methods and attributes in the Server class
print("Available in Server class:")
for name, obj in inspect.getmembers(Server):
    if not name.startswith("_"):  # Skip private/internal items
        print(f"- {name}: {type(obj)}")
