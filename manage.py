#!/usr/bin/env python 
import os 
import sys
from app import create_app, db
from app.models import User, Role

app = create_app(os.getenv('FLASK_CONFIG') or 'default') 

@app.cli.command()
def shell():
    """Run a Python shell in the context of the application."""
    import code
    import readline
    from rlcompleter import Completer
    
    # Create a dictionary with the application context
    context = {'app': app, 'db': db, 'User': User, 'Role': Role}
    
    # Start the shell
    code.interact(local=context)

@app.cli.command()
def create_db():
    """Create database tables."""
    with app.app_context():
        db.create_all()
        print('Database tables created successfully!')

if __name__ == '__main__': 
    # 启动应用
    app.run()