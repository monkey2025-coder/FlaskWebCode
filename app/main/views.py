from datetime import datetime 
from flask import Flask, render_template, session
from . import main 
from app.models import User


@main.route('/') 
def index(): 
    return render_template('index.html', 
        name = session.get('name'), 
        current_time=datetime.utcnow())

@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)