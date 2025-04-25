from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from calendar import monthrange
from app.models import Deal, Lead, User, Interaction, Contact, Task, Project
from sqlalchemy import func, extract, case, and_
from app.extensions import db

bp = Blueprint('dashboard', __name__)

def get_empty_chart_data():
    """Return empty chart data structure"""
    return {
        'deal_progress_data': {
            'labels': [],
            'datasets': [
                {'label': 'Lead', 'data': [], 'backgroundColor': '#6c757d'},
                {'label': 'Qualified', 'data': [], 'backgroundColor': '#0d6efd'},
                {'label': 'Proposal', 'data': [], 'backgroundColor': '#ffc107'},
                {'label': 'Negotiation', 'data': [], 'backgroundColor': '#0dcaf0'},
                {'label': 'Customer', 'data': [], 'backgroundColor': '#198754'}
            ]
        },
        'leads_data': {
            'labels': [],
            'values': []
        },
        'forecast_data': {
            'labels': [],
            'values': []
        },
        'interaction_data': {
            'dates': [],
            'counts': []
        },
        'recent_interactions': [],
        'pipeline_stages': [],
        'win_rate': 0,
        'revenue_forecast': 0,
        'total_contacts': 0,
        'total_interactions': 0,
        'pending_tasks': 0,
        'active_projects': 0
    }

@bp.route('/dashboard')
@login_required
def index():
    try:
        # Initialize empty data structure
        data = get_empty_chart_data()
        
        # Get current date info
        today = datetime.now()
        current_month = today.month
        current_year = today.year

        # Get basic counts
        data['total_contacts'] = Contact.query.count()
        data['total_interactions'] = Interaction.query.count()
        data['pending_tasks'] = Task.query.filter_by(status='pending').count()
        data['active_projects'] = Project.query.filter_by(status='active').count()

        # Debug: Print current date info
        print(f"Current date: {today}")
        print(f"Current year: {current_year}")
        
        # Get recent interactions
        try:
            recent_interactions = Interaction.query.filter(
                Interaction.created_by_id == current_user.id
            ).order_by(
                Interaction.created_at.desc()
            ).limit(5).all()
            
            data['recent_interactions'] = recent_interactions
            
            # Calculate interaction trends (last 7 days)
            trend_dates = []
            trend_counts = []
            
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                trend_dates.append(date.strftime('%a'))
                
                count = Interaction.query.filter(
                    Interaction.created_by_id == current_user.id,
                    func.date(Interaction.created_at) == date.date()
                ).count()
                
                trend_counts.append(count)
            
            data['interaction_data'] = {
                'dates': trend_dates,
                'counts': trend_counts
            }
            
        except Exception as e:
            print(f"Error fetching interaction data: {e}")  # Log the error properly in production

        # Calculate leads by user
        try:
            leads_by_user = db.session.query(
                User.full_name.label('name'),
                func.count(Lead.id).label('count')
            ).join(
                Lead, 
                (Lead.created_by_id == User.id) & 
                (extract('year', Lead.created_at) == current_year)
            ).group_by(
                User.id, 
                User.full_name
            ).order_by(
                func.count(Lead.id).desc()
            ).limit(5).all()

            if leads_by_user:
                data['leads_data'] = {
                    'labels': [user.name for user in leads_by_user],
                    'values': [user.count for user in leads_by_user]
                }
        except Exception as e:
            print(f"Error fetching leads data: {e}")  # Log the error properly in production
            
        # Calculate deal progress data with actual stages and status (open/won/lost)
        try:
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
            print('Deal Progress Months:', [ (today - timedelta(days=30*i)).strftime('%b') for i in range(4, -1, -1)])
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
                    print(f"Month: {target_date.strftime('%b')}, Stage: {ds['stage']}, Status: {ds['status']}, Count: {count}")
                    ds['data'].append(count)
            data['deal_progress_data'] = {
                'labels': months,
                'datasets': [
                    {
                        'label': ds['label'],
                        'data': ds['data'],
                        'backgroundColor': ds['backgroundColor']
                    } for ds in datasets
                ]
            }
            print('Final deal_progress_data:', data['deal_progress_data'])
        except Exception as e:
            print(f"Error calculating deal progress: {e}")
            print(f"Error details: {str(e)}")
            # Keep the empty data structure if there's an error
        
        # Calculate pipeline stages and conversion rates with actual data
        try:
            # Get total deals for the year
            total_deals = Contact.query.filter(
                extract('year', Contact.created_at) == current_year
            ).count() or 1  # Avoid division by zero
            
            # Calculate won deals and win rate
            won_deals = Contact.query.filter(
                and_(
                    extract('year', Contact.created_at) == current_year,
                    Contact.stage == 'customer'
                )
            ).count()
            
            data['win_rate'] = round((won_deals / total_deals * 100))
            
            # Calculate conversion rates for each stage
            stage_metrics = []
            stages = ['lead', 'qualified', 'proposal', 'negotiation', 'customer']
            previous_stage_count = total_deals
            
            for stage in stages:
                stage_count = Contact.query.filter(
                    and_(
                        extract('year', Contact.created_at) == current_year,
                        Contact.stage == stage
                    )
                ).count()
                
                # Calculate average deal value and probability for this stage
                stage_stats = Contact.query.with_entities(
                    func.avg(Contact.deal_value).label('avg_value'),
                    func.avg(Contact.probability).label('avg_probability')
                ).filter(
                    and_(
                        extract('year', Contact.created_at) == current_year,
                        Contact.stage == stage
                    )
                ).first()
                
                # Calculate conversion rate from previous stage
                conversion_rate = round((stage_count / previous_stage_count * 100) if previous_stage_count > 0 else 0)
                previous_stage_count = stage_count if stage_count > 0 else previous_stage_count
                
                stage_metrics.append({
                    'name': stage.replace('_', ' ').title(),
                    'count': stage_count,
                    'conversion_rate': conversion_rate,
                    'avg_value': float(stage_stats.avg_value or 0),
                    'avg_probability': float(stage_stats.avg_probability or 0)
                })
            
            data['pipeline_stages'] = stage_metrics
            
        except Exception as e:
            print(f"Error calculating pipeline metrics: {e}")
            print(f"Error details: {str(e)}")
        
        # Calculate revenue forecast based on actual probabilities
        try:
            future_deals = Contact.query.filter(
                Contact.stage.in_(['qualified', 'proposal', 'negotiation']),
                Contact.expected_close_date <= today + timedelta(days=30)
            ).all()
            
            # Use actual probabilities from contacts
            data['revenue_forecast'] = sum(
                (deal.deal_value or 0) * ((deal.probability or 0) / 100)
                for deal in future_deals
            )
            
            # Generate forecast data for the next 30 days
            forecast_labels = []
            forecast_values = []
            daily_forecast = data['revenue_forecast'] / 30 if data['revenue_forecast'] > 0 else 0
            
            for i in range(30):
                date = today + timedelta(days=i)
                forecast_labels.append(date.strftime('%d %b'))
                forecast_values.append(daily_forecast * (i + 1))
            
            data['forecast_data'] = {
                'labels': forecast_labels,
                'values': forecast_values
            }
            
        except Exception as e:
            print(f"Error calculating revenue forecast: {e}")
            print(f"Error details: {str(e)}")
        
        # Ensure all data is properly initialized
        required_keys = [
            'deal_progress_data', 'leads_data', 'forecast_data', 'interaction_data',
            'recent_interactions', 'pipeline_stages', 'win_rate', 'revenue_forecast',
            'total_contacts', 'total_interactions', 'pending_tasks', 'active_projects'
        ]
        empty_data = get_empty_chart_data()
        for key in required_keys:
            if key not in data or data[key] is None:
                print(f"Warning: {key} is missing or None, setting to default.")
                data[key] = empty_data[key]
        print("Final dashboard data context:", data)
        
        # Debug: Print deal progress data before rendering
        print('Deal Progress Data sent to template:', data['deal_progress_data'])

        # Debug: List all contacts created in the last 5 months
        five_months_ago = today - timedelta(days=30*4)
        recent_contacts = Contact.query.filter(Contact.created_at >= five_months_ago).all()
        print('Contacts created in the last 5 months:')
        for c in recent_contacts:
            print(f'  ID: {c.id}, Name: {c.first_name} {c.last_name}, Created: {c.created_at}, Stage: {c.stage}')

        return render_template('dashboard.html', **data)
    except Exception as e:
        print(f"Error in dashboard: {e}")
        print(f"Error details: {str(e)}")
        return render_template('dashboard.html', **get_empty_chart_data()) 