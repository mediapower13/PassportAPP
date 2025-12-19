"""
Error handlers for PassportApp
Handle common errors and exceptions
"""

from flask import render_template, jsonify, request


def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Resource not found',
                'status': 404
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f'Internal error: {error}')
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'status': 500
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'status': 403
            }), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 errors"""
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'status': 401
            }), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 errors"""
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Bad request',
                'status': 400
            }), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unexpected exceptions"""
        app.logger.error(f'Unhandled exception: {error}')
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'An unexpected error occurred',
                'status': 500
            }), 500
        return render_template('errors/500.html'), 500
