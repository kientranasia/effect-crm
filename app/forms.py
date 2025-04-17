from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Optional, URL

class LeadForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    job_title = StringField('Job Title', validators=[Optional()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    industry = SelectField('Industry', choices=[
        ('', 'Select Industry'),
        ('Technology', 'Technology'),
        ('Healthcare', 'Healthcare'),
        ('Finance', 'Finance'),
        ('Manufacturing', 'Manufacturing'),
        ('Retail', 'Retail'),
        ('Other', 'Other')
    ])
    company_size = SelectField('Company Size', choices=[
        ('', 'Select Size'),
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-200', '51-200'),
        ('201-500', '201-500'),
        ('501-1000', '501-1000'),
        ('1000+', '1000+')
    ])
    website = StringField('Website', validators=[Optional(), URL()])
    source = SelectField('Source', choices=[
        ('', 'Select Source'),
        ('Website', 'Website'),
        ('Referral', 'Referral'),
        ('Social Media', 'Social Media'),
        ('Email Campaign', 'Email Campaign'),
        ('Other', 'Other')
    ])
    status = SelectField('Status', choices=[
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost')
    ])
    notes = TextAreaField('Notes', validators=[Optional()])
    interested_in = TextAreaField('Interested In', validators=[Optional()])
    requirements = TextAreaField('Requirements', validators=[Optional()])
    budget = StringField('Budget', validators=[Optional()])
    timeline = StringField('Timeline', validators=[Optional()]) 