from typing import Any, Dict
from datetime import datetime, timedelta
from calendar import monthrange
from flask_login import current_user
from sqlalchemy import and_
from app.models import Contact
from app.extensions import db
import logging

def get_deal_progress_data(user) -> Dict[str, Any]:
    """
    Aggregate deal progress data for the dashboard.
    Returns a dict with 'labels' and 'datasets' for the last 5 months,
    counting contacts by (stage, status).
    """
    try:
        today = datetime.now()
        months = []
        stages = [
            ('lead', 'Lead', '#6c757d'),
            ('prospect', 'Prospect', '#17a2b8'),
            ('qualified', 'Qualified', '#0d6efd'),
            ('proposal', 'Proposal', '#ffc107'),
            ('negotiation', 'Negotiation', '#0dcaf0'),
            ('customer', 'Customer', '#198754'),
            ('closed_won', 'Closed Won', '#198754'),
            ('closed_lost', 'Closed Lost', '#dc3545'),
        ]
        status_map = {
            'open': {'lead', 'prospect', 'qualified', 'proposal', 'negotiation'},
            'won': {'customer', 'closed_won'},
            'lost': {'closed_lost'}
        }
        status_colors = {
            'open': '',
            'won': '#198754',
            'lost': '#dc3545'
        }
        datasets = []
        for stage_key, stage_label, stage_color in stages:
            for status, stage_set in status_map.items():
                if stage_key in stage_set:
                    label = f"{stage_label} - {status.title()}"
                    color = status_colors[status] if status_colors[status] else stage_color
                    datasets.append({
                        'stage': stage_key,
                        'status': status,
                        'label': label,
                        'backgroundColor': color,
                        'data': []
                    })
        logging.info('Deal Progress Months: %s', [ (today - timedelta(days=30*i)).strftime('%b') for i in range(4, -1, -1)])
        for i in range(4, -1, -1):
            target_date = today - timedelta(days=30*i)
            month_start = datetime(target_date.year, target_date.month, 1)
            month_end = datetime(target_date.year, target_date.month, monthrange(target_date.year, target_date.month)[1])
            months.append(target_date.strftime('%b'))
            for ds in datasets:
                count = Contact.query.filter(
                    and_(
                        Contact.created_at >= month_start,
                        Contact.created_at <= month_end,
                        Contact.stage == ds['stage']
                    )
                ).count()
                logging.info(f"Month: {target_date.strftime('%b')}, Stage: {ds['stage']}, Status: {ds['status']}, Count: {count}")
                ds['data'].append(count)
        result = {
            'labels': months,
            'datasets': [
                {
                    'label': ds['label'],
                    'data': ds['data'],
                    'backgroundColor': ds['backgroundColor']
                } for ds in datasets
            ]
        }
        logging.info('Final deal_progress_data: %s', result)
        return result
    except Exception as e:
        logging.error(f"Error in get_deal_progress_data: {e}")
        return {'labels': [], 'datasets': []}

def get_revenue_forecast_data(user, days: int = 30) -> Dict[str, Any]:
    """
    Aggregate revenue forecast for the dashboard.
    Returns a dict with 'revenue_forecast' (float) and 'forecast_data' (labels/values for chart).
    """
    try:
        today = datetime.now()
        # Only consider deals with a valid expected_close_date in the next N days
        future_deals = Contact.query.filter(
            Contact.stage.in_(['qualified', 'proposal', 'negotiation']),
            Contact.expected_close_date != None,
            Contact.expected_close_date <= today + timedelta(days=days)
        ).all()
        if not future_deals:
            logging.warning('No future deals found for revenue forecast.')
        # Calculate weighted revenue forecast
        revenue_forecast = sum(
            (deal.deal_value or 0) * ((deal.probability or 0) / 100)
            for deal in future_deals
        )
        # Generate forecast data for the next N days
        forecast_labels = []
        forecast_values = []
        daily_forecast = revenue_forecast / days if revenue_forecast > 0 else 0
        for i in range(days):
            date = today + timedelta(days=i)
            forecast_labels.append(date.strftime('%d %b'))
            forecast_values.append(daily_forecast * (i + 1))
        result = {
            'revenue_forecast': revenue_forecast,
            'forecast_data': {
                'labels': forecast_labels,
                'values': forecast_values
            }
        }
        logging.info('Final revenue_forecast_data: %s', result)
        return result
    except Exception as e:
        logging.error(f"Error in get_revenue_forecast_data: {e}")
        return {'revenue_forecast': 0, 'forecast_data': {'labels': [], 'values': []}} 