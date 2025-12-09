from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Passport, db
from datetime import datetime, timedelta
import re

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
main_bp = Blueprint('main', __name__)

# Main routes
@main_bp.route('/')
@login_required
def index():
    # Get passport statistics
    passport_count = Passport.query.filter_by(user_id=current_user.id).count()
    
    # Get expiring soon (within 90 days)
    ninety_days_later = datetime.utcnow().date() + timedelta(days=90)
    expiring_count = Passport.query.filter(
        Passport.user_id == current_user.id,
        Passport.expiry_date <= ninety_days_later,
        Passport.expiry_date >= datetime.utcnow().date()
    ).count()
    
    return render_template('dashboard.html', 
                         user=current_user, 
                         passport_count=passport_count,
                         expiring_count=expiring_count)

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)

@main_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form.get('name')
    bio = request.form.get('bio')
    
    if name:
        current_user.name = name
    if bio:
        current_user.bio = bio
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))

# Authentication routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        
        errors = []
        
        # Validation
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Please enter a valid email address')
        if not username:
            errors.append('Username is required')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if password != password2:
            errors.append('Passwords do not match')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', 
                                 name=name, 
                                 email=email, 
                                 username=username)
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            username=username
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return render_template('login.html', username=username)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html', username=username)
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))
