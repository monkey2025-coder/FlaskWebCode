#!/usr/bin/env python 
import os 
from app import create_app 

app = create_app(os.getenv('FLASK_CONFIG') or 'default') 

@app.cli.command()
def shell():
    """Run a Python shell in the context of the application."""
    import code
    import readline
    from rlcompleter import Completer
    
    # Create a dictionary with the application context
    context = {'app': app}
    
    # Start the shell
    code.interact(local=context)

if __name__ == '__main__': 
    app.run()