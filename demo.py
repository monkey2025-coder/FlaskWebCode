# -*- encoding: utf-8 -*-
'''
file       :demo.py
Description:这是一个简单的Flask应用
Date       :2026/02/25 16:24:19
Author     :czy
version    :v0.01
email      :1060324818@qq.com
'''

from flask import Flask, render_template, session, redirect, url_for, flash 
from flask_bootstrap import Bootstrap  
from flask_moment import Moment 
from datetime import datetime 
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField 
from wtforms.validators import InputRequired 


class NameForm(FlaskForm): 
    name = StringField('What is your name?', validators=[InputRequired()]) 
    submit = SubmitField('Submit')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/', methods=['GET', 'POST']) 
def index(): 
    form = NameForm() 
    if form.validate_on_submit(): 
        old_name = session.get('name') 
        if old_name is not None and old_name != form.name.data: 
            flash('Looks like you have changed your name!') 
        session['name'] = form.name.data 
        return redirect(url_for('index')) 
    return render_template('index.html', form=form, name=session.get('name'), current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404) 
def page_not_found(e): 
    return render_template('404.html'), 404 

@app.errorhandler(500) 
def internal_server_error(e): 
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)