"""
File upload validator for PassportApp
Validate uploaded files for security and compliance
"""

import os
import mimetypes
import hashlib
from datetime import datetime
import magic


class FileUploadValidator:
    """Validate file uploads"""
    
    def __init__(self):
        self.allowed_extensions = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'document': ['pdf', 'doc', 'docx'],
            'data': ['json', 'csv', 'xml']
        }
        
        self.allowed_mimetypes = {
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/json',
            'text/csv',
            'application/xml'
        }
        
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        self.min_file_size = 1  # 1 byte
    
    def validate_file(self, file_path, file_type='image'):
        """Validate uploaded file"""
        errors = []
        warnings = []
        
        # Check file exists
        if not os.path.exists(file_path):
            errors.append('File does not exist')
            return False, errors, warnings
        
        # Check file size
        file_size = os.path.getsize(file_path)
        
        if file_size > self.max_file_size:
            errors.append(f'File too large: {file_size} bytes (max: {self.max_file_size})')
        
        if file_size < self.min_file_size:
            errors.append(f'File too small: {file_size} bytes')
        
        # Check extension
        ext = self._get_extension(file_path).lower()
        
        if file_type in self.allowed_extensions:
            allowed = self.allowed_extensions[file_type]
            if ext not in allowed:
                errors.append(f'Invalid extension: {ext} (allowed: {", ".join(allowed)})')
        
        # Check MIME type
        detected_mime = self._detect_mimetype(file_path)
        
        if detected_mime not in self.allowed_mimetypes:
            errors.append(f'Invalid MIME type: {detected_mime}')
        
        # Check file extension matches MIME type
        if not self._extension_matches_mime(ext, detected_mime):
            warnings.append(f'Extension {ext} does not match MIME type {detected_mime}')
        
        # Scan for malicious content
        is_safe, scan_msg = self._scan_file_content(file_path, file_type)
        if not is_safe:
            errors.append(f'Security scan failed: {scan_msg}')
        
        return len(errors) == 0, errors, warnings
    
    def validate_image(self, file_path):
        """Validate image file"""
        valid, errors, warnings = self.validate_file(file_path, 'image')
        
        if not valid:
            return False, errors, warnings
        
        # Additional image validation
        try:
            from PIL import Image
            
            img = Image.open(file_path)
            
            # Check dimensions
            width, height = img.size
            
            if width > 10000 or height > 10000:
                warnings.append(f'Image dimensions very large: {width}x{height}')
            
            if width < 10 or height < 10:
                errors.append(f'Image dimensions too small: {width}x{height}')
            
            # Check format
            if img.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
                errors.append(f'Unsupported image format: {img.format}')
            
        except Exception as e:
            errors.append(f'Failed to validate image: {str(e)}')
        
        return len(errors) == 0, errors, warnings
    
    def validate_pdf(self, file_path):
        """Validate PDF file"""
        valid, errors, warnings = self.validate_file(file_path, 'document')
        
        if not valid:
            return False, errors, warnings
        
        # Additional PDF validation
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                
                # Check page count
                page_count = len(pdf.pages)
                
                if page_count > 100:
                    warnings.append(f'PDF has many pages: {page_count}')
                
                if page_count == 0:
                    errors.append('PDF has no pages')
        
        except Exception as e:
            errors.append(f'Failed to validate PDF: {str(e)}')
        
        return len(errors) == 0, errors, warnings
    
    def calculate_file_hash(self, file_path, algorithm='sha256'):
        """Calculate file hash"""
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def sanitize_filename(self, filename):
        """Sanitize filename"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 100:
            name = name[:100]
        
        return f'{name}{ext}'
    
    def generate_safe_filename(self, original_filename):
        """Generate safe unique filename"""
        sanitized = self.sanitize_filename(original_filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_suffix = os.urandom(4).hex()
        
        name, ext = os.path.splitext(sanitized)
        
        return f'{name}_{timestamp}_{random_suffix}{ext}'
    
    def _get_extension(self, file_path):
        """Get file extension"""
        return os.path.splitext(file_path)[1].lstrip('.')
    
    def _detect_mimetype(self, file_path):
        """Detect MIME type"""
        try:
            # Try python-magic first
            mime = magic.from_file(file_path, mime=True)
            return mime
        except:
            # Fallback to mimetypes
            mime, _ = mimetypes.guess_type(file_path)
            return mime or 'application/octet-stream'
    
    def _extension_matches_mime(self, ext, mime):
        """Check if extension matches MIME type"""
        ext_mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'json': 'application/json',
            'csv': 'text/csv',
            'xml': 'application/xml'
        }
        
        expected_mime = ext_mime_map.get(ext)
        
        return expected_mime == mime
    
    def _scan_file_content(self, file_path, file_type):
        """Scan file for malicious content"""
        # Basic content scanning
        
        if file_type == 'image':
            # Check for embedded scripts in image metadata
            try:
                from PIL import Image
                img = Image.open(file_path)
                
                # Check EXIF data for suspicious content
                exif = img.getexif()
                if exif:
                    for tag, value in exif.items():
                        if isinstance(value, str):
                            if '<script' in value.lower() or 'javascript:' in value.lower():
                                return False, 'Suspicious content in image metadata'
            except:
                pass
        
        # Check file header/magic bytes
        with open(file_path, 'rb') as f:
            header = f.read(512)
            
            # Look for script tags
            if b'<script' in header.lower() or b'javascript:' in header.lower():
                return False, 'Suspicious script content detected'
            
            # Look for executable signatures
            executable_signatures = [
                b'MZ',  # DOS/Windows executable
                b'\x7fELF',  # Linux executable
                b'\xca\xfe\xba\xbe'  # macOS executable
            ]
            
            for sig in executable_signatures:
                if header.startswith(sig):
                    return False, 'Executable file detected'
        
        return True, 'File appears safe'


# Global file validator
file_validator = FileUploadValidator()


def validate_upload(file_path, file_type='image'):
    """Validate uploaded file"""
    return file_validator.validate_file(file_path, file_type)


def validate_image_upload(file_path):
    """Validate uploaded image"""
    return file_validator.validate_image(file_path)


def validate_pdf_upload(file_path):
    """Validate uploaded PDF"""
    return file_validator.validate_pdf(file_path)


def safe_save_upload(file_obj, upload_dir='uploads', file_type='image'):
    """Safely save uploaded file"""
    # Generate safe filename
    original_filename = file_obj.filename
    safe_filename = file_validator.generate_safe_filename(original_filename)
    
    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, safe_filename)
    file_obj.save(file_path)
    
    # Validate
    valid, errors, warnings = file_validator.validate_file(file_path, file_type)
    
    if not valid:
        # Delete invalid file
        os.remove(file_path)
        return False, None, errors, warnings
    
    # Calculate hash
    file_hash = file_validator.calculate_file_hash(file_path)
    
    return True, {
        'path': file_path,
        'filename': safe_filename,
        'original_filename': original_filename,
        'size': os.path.getsize(file_path),
        'hash': file_hash,
        'warnings': warnings
    }, [], warnings


class UploadQuota:
    """Manage upload quotas per user"""
    
    def __init__(self):
        self.quotas = {}
        self.default_quota = 100 * 1024 * 1024  # 100MB per user
    
    def check_quota(self, user_id, file_size):
        """Check if user has quota for upload"""
        used = self.quotas.get(user_id, 0)
        
        if used + file_size > self.default_quota:
            return False, f'Quota exceeded: {used + file_size} / {self.default_quota}'
        
        return True, 'Quota available'
    
    def increment_quota(self, user_id, file_size):
        """Increment used quota"""
        self.quotas[user_id] = self.quotas.get(user_id, 0) + file_size
    
    def get_quota_info(self, user_id):
        """Get quota information"""
        used = self.quotas.get(user_id, 0)
        
        return {
            'used': used,
            'total': self.default_quota,
            'remaining': self.default_quota - used,
            'percent_used': (used / self.default_quota) * 100
        }


# Global upload quota manager
upload_quota = UploadQuota()
