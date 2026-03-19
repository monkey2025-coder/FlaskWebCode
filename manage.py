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
    # 检查是否有命令参数
    if len(sys.argv) > 1 and sys.argv[1] in ['create_db', 'shell']:
        # 执行 Flask CLI 命令
        from flask.cli import main
        sys.exit(main())
    else:
        # 启动应用
        app.run()