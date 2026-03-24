import sys

try:
    from app import app
    print("App imported successfully")
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
