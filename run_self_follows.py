from app import app, db
from app.models import User

with app.app_context():
    try:
        User.add_self_follows()
        print("Self follows added successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
