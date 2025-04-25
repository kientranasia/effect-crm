from functools import wraps
from flask import flash, redirect, url_for, request, jsonify
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    If a non-admin user tries to access a protected route, they will be
    redirected to the main page with a flash message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """
    Decorator to check if the current user has the required permission.
    If the user doesn't have the permission, they will be redirected to the dashboard
    with a flash message.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if not current_user.has_permission(permission):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_exceptions(f):
    """
    Decorator to handle exceptions in route functions.
    If an exception occurs, it will return a JSON response with an error message
    for API routes, or redirect to the previous page with a flash message for
    regular routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Check if the request wants JSON response
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
            # For regular routes, flash the error and redirect back
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(request.referrer or url_for('main.dashboard'))
    return decorated_function 