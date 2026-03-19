from datetime import datetime 
from flask import Flask, render_template, session, redirect, url_for, flash
from . import main 
from .forms import NameForm 
from app.models import User
from app import db 


@main.route('/', methods=['GET', 'POST']) 
def index(): 
    form = NameForm() 
    if form.validate_on_submit(): 
        user = User.query.filter_by(username=form.name.data).first() 
        if user is None: 
            user = User(username = form.name.data) 
            db.session.add(user) 
            session['known'] = False 
        else: 
            session['known'] = True 
        session['name'] = form.name.data 
        form.name.data = '' 
        return redirect(url_for('main.index'), code=303)
    return render_template('index.html', 
        form = form, name = session.get('name'), 
        known = session.get('known', False), current_time=datetime.utcnow())

@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)