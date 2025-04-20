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