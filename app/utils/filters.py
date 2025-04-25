from datetime import datetime

def timeago(date):
    """Convert a datetime to a human readable string like '2 days ago'"""
    if not date:
        return ''
        
    now = datetime.utcnow()
    diff = now - date

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = diff.days

    if seconds < 60:
        return 'just now'
    elif minutes < 60:
        return f'{int(minutes)} minutes ago'
    elif hours < 24:
        return f'{int(hours)} hours ago'
    elif days == 1:
        return 'yesterday'
    elif days < 7:
        return f'{days} days ago'
    elif days < 30:
        weeks = days // 7
        return f'{weeks} weeks ago'
    elif days < 365:
        months = days // 30
        return f'{months} months ago'
    else:
        years = days // 365
        return f'{years} years ago'

def format_currency(value):
    """Format a number as currency with thousands separator and 2 decimal places"""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "0.00"

def parse_datetime(value):
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return value
    return value

def strftime(value, fmt):
    if value is None:
        return ''
    try:
        return value.strftime(fmt)
    except Exception:
        return value

def register_filters(app):
    """Register custom template filters"""
    app.jinja_env.filters['timeago'] = timeago
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['parse_datetime'] = parse_datetime
    app.jinja_env.filters['strftime'] = strftime 