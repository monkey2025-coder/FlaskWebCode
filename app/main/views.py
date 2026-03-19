from datetime import datetime 
from flask import Flask, render_template, session
from . import main 
from app.models import User, Role
from .forms import EditProfileForm, EditProfileAdminForm
from app import db
from flask_login import login_required, current_user
from flask import redirect, url_for, flash
from app.decorators import admin_required



@main.route('/') 
def index(): 
    return render_template('index.html', 
        name = session.get('name'), 
        current_time=datetime.utcnow())

@main.route('/user/<username>') 
def user(username): 
    user = User.query.filter_by(username=username).first() 
    if user is None: 
        abort(404) 
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST']) 
@login_required 
def edit_profile(): 
    form = EditProfileForm() 
    if form.validate_on_submit(): 
        current_user.name = form.name.data 
        current_user.location = form.location.data 
        current_user.about_me = form.about_me.data 
        db.session.add(current_user) 
        db.session.commit()
        flash('Your profile has been updated.') 
        return redirect(url_for('.user', username=current_user.username)) 
    form.name.data = current_user.name 
    form.location.data = current_user.location 
    form.about_me.data = current_user.about_me 
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST']) 
@login_required 
@admin_required 
def edit_profile_admin(id): 
    user = User.query.get_or_404(id) 
    form = EditProfileAdminForm(user=user) 
    if form.validate_on_submit(): 
        user.email = form.email.data 
        user.username = form.username.data 
        user.role = Role.query.get(form.role.data) 
        user.name = form.name.data 
        user.location = form.location.data 
        user.about_me = form.about_me.data 
        db.session.add(user) 
        db.session.commit()
        flash('The profile has been updated.') 
        return redirect(url_for('.user', username=user.username)) 
    form.email.data = user.email 
    form.username.data = user.username 
    form.role.data = user.role_id 
    form.name.data = user.name 
    form.location.data = user.location 
    form.about_me.data = user.about_me 
    return render_template('edit_profile.html', form=form, user=user)