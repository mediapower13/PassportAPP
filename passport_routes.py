"""
Passport management routes
Handles secure storage and retrieval of passport documents
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Passport
from encryption import get_encryption_service
from passport_scanner import get_passport_scanner
from datetime import datetime
import base64

passport_bp = Blueprint('passport', __name__, url_prefix='/passport')


@passport_bp.route('/')
@login_required
def index():
    """Display all user's passports"""
    passports = Passport.query.filter_by(user_id=current_user.id).all()
    
    # Decrypt sensitive data for display
    encryption = get_encryption_service()
    for passport in passports:
        try:
            passport.passport_number_display = encryption.decrypt(passport.passport_number)
            passport.full_name_display = encryption.decrypt(passport.full_name)
            passport.date_of_birth_display = encryption.decrypt(passport.date_of_birth) if passport.date_of_birth else None
        except:
            passport.passport_number_display = "****"
            passport.full_name_display = "****"
    
    return render_template('passport_list.html', passports=passports)


@passport_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new passport"""
    if request.method == 'POST':
        try:
            encryption = get_encryption_service()
            
            # Get form data
            passport_number = request.form.get('passport_number', '').strip()
            full_name = request.form.get('full_name', '').strip()
            nationality = request.form.get('nationality', '').strip()
            date_of_birth = request.form.get('date_of_birth', '').strip()
            place_of_birth = request.form.get('place_of_birth', '').strip()
            
            # Validate required fields
            if not passport_number or not full_name:
                flash('Passport number and full name are required', 'error')
                return redirect(url_for('passport.add'))
            gender = request.form.get('gender', '').strip()
            issue_date_str = request.form.get('issue_date', '').strip()
            expiry_date_str = request.form.get('expiry_date', '').strip()
            issuing_country = request.form.get('issuing_country', '').strip()
            notes = request.form.get('notes', '').strip()
            is_primary = request.form.get('is_primary') == 'on'
            
            # Validation
            if not all([passport_number, full_name, nationality, expiry_date_str, issuing_country]):
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('passport.add'))
            
            # Additional validation
            if len(passport_number) > 50:
                flash('Passport number is too long', 'danger')
                return redirect(url_for('passport.add'))
            
            if len(full_name) > 255:
                flash('Full name is too long', 'danger')
                return redirect(url_for('passport.add'))
            
            # Convert dates with error handling
            try:
                issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date() if issue_date_str else None
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD', 'danger')
                return redirect(url_for('passport.add'))
            
            # Check if expiry date is valid
            if expiry_date < datetime.utcnow().date():
                flash('Passport has already expired. Please renew it.', 'warning')
            
            # Handle image upload
            photo_data = None
            document_image = None
            
            if 'photo' in request.files:
                photo_file = request.files['photo']
                if photo_file and photo_file.filename:
                    photo_bytes = photo_file.read()
                    photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
                    photo_data = encryption.encrypt(photo_base64)
            
            if 'document_image' in request.files:
                doc_file = request.files['document_image']
                if doc_file and doc_file.filename:
                    doc_bytes = doc_file.read()
                    doc_base64 = base64.b64encode(doc_bytes).decode('utf-8')
                    document_image = encryption.encrypt(doc_base64)
            
            # If setting as primary, unset other primary passports
            if is_primary:
                Passport.query.filter_by(user_id=current_user.id, is_primary=True).update({'is_primary': False})
            
            # Create new passport with encrypted data
            new_passport = Passport(
                user_id=current_user.id,
                passport_number=encryption.encrypt(passport_number),
                full_name=encryption.encrypt(full_name),
                nationality=nationality,
                date_of_birth=encryption.encrypt(date_of_birth) if date_of_birth else None,
                place_of_birth=place_of_birth,
                gender=gender,
                issue_date=issue_date,
                expiry_date=expiry_date,
                issuing_country=issuing_country,
                photo_data=photo_data,
                document_image=document_image,
                notes=notes,
                is_primary=is_primary
            )
            
            db.session.add(new_passport)
            db.session.commit()
            
            flash('Passport added successfully and securely encrypted!', 'success')
            return redirect(url_for('passport.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding passport: {str(e)}', 'danger')
            return redirect(url_for('passport.add'))
    
    return render_template('passport_add.html')


@passport_bp.route('/view/<int:passport_id>')
@login_required
def view(passport_id):
    """View passport details"""
    passport = Passport.query.get_or_404(passport_id)
    
    # Ensure user owns this passport
    if passport.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('passport.index'))
    
    # Decrypt sensitive data
    encryption = get_encryption_service()
    try:
        passport.passport_number_display = encryption.decrypt(passport.passport_number)
        passport.full_name_display = encryption.decrypt(passport.full_name)
        passport.date_of_birth_display = encryption.decrypt(passport.date_of_birth) if passport.date_of_birth else None
        
        # Decrypt images
        if passport.photo_data:
            photo_encrypted = encryption.decrypt(passport.photo_data)
            passport.photo_display = f"data:image/jpeg;base64,{photo_encrypted}"
        else:
            passport.photo_display = None
        
        if passport.document_image:
            doc_encrypted = encryption.decrypt(passport.document_image)
            passport.document_display = f"data:image/jpeg;base64,{doc_encrypted}"
        else:
            passport.document_display = None
            
    except Exception as e:
        flash(f'Error decrypting passport data: {str(e)}', 'danger')
        return redirect(url_for('passport.index'))
    
    return render_template('passport_view.html', passport=passport)


@passport_bp.route('/delete/<int:passport_id>', methods=['POST'])
@login_required
def delete(passport_id):
    """Delete a passport"""
    passport = Passport.query.get_or_404(passport_id)
    
    # Ensure user owns this passport
    if passport.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('passport.index'))
    
    try:
        db.session.delete(passport)
        db.session.commit()
        flash('Passport deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting passport: {str(e)}', 'danger')
    
    return redirect(url_for('passport.index'))


@passport_bp.route('/scan', methods=['POST'])
@login_required
def scan():
    """Scan passport using OCR"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image provided'})
        
        image_file = request.files['image']
        if not image_file or not image_file.filename:
            return jsonify({'success': False, 'message': 'Invalid image'})
        
        # Read image data
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Scan passport
        scanner = get_passport_scanner()
        result = scanner.extract_mrz_from_image(image_base64)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@passport_bp.route('/check-expiry')
@login_required
def check_expiry():
    """Check which passports are expiring soon"""
    passports = Passport.query.filter_by(user_id=current_user.id).all()
    
    expiring_soon = []
    expired = []
    
    for passport in passports:
        if passport.is_expired():
            expired.append(passport)
        elif passport.needs_renewal():
            expiring_soon.append(passport)
    
    return render_template('passport_expiry.html', 
                         expiring_soon=expiring_soon, 
                         expired=expired)
