from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, TimeField, SubmitField, PasswordField, BooleanField, HiddenField, FloatField, SelectMultipleField
from wtforms import validators
from wtforms.validators import DataRequired, Email, Optional, URL, Length, EqualTo
import json
from app.models import Organization

def empty_to_none(value):
    return None if value in (None, '', ' ') else value

class ContactForm(FlaskForm):
    # Contact Information
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    alternate_email = StringField('Alternate Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    mobile = StringField('Mobile', validators=[Optional()])
    work_phone = StringField('Work Phone', validators=[Optional()])
    home_phone = StringField('Home Phone', validators=[Optional()])
    title = StringField('Job Title', validators=[Optional()])
    
    # Overview and Summary
    summary = TextAreaField('Summary Overview', validators=[Optional()])
    linkedin_bio = TextAreaField('LinkedIn Bio', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    # Pipeline tracking
    source = SelectField('Source', choices=[
        ('', 'Select Source'),
        ('Website', 'Website'),
        ('Referral', 'Referral'),
        ('Social Media', 'Social Media'),
        ('Email Campaign', 'Email Campaign'),
        ('Other', 'Other')
    ], validators=[Optional()])
    stage = SelectField('Stage', choices=[
        ('lead', 'Lead'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('customer', 'Customer')
    ], validators=[Optional()])
    source_origin = StringField('Source Origin', validators=[Optional()])
    source_channel = StringField('Source Channel', validators=[Optional()])
    deal_value = FloatField('Deal Value', [validators.Optional()], filters=[empty_to_none])
    probability = FloatField('Probability', [validators.Optional()], filters=[empty_to_none])
    interested_in = TextAreaField('Interested In', validators=[Optional()])
    requirements = TextAreaField('Requirements', validators=[Optional()])
    budget = StringField('Budget', validators=[Optional()])
    
    # Address Information
    address_line1 = StringField('Address Line 1', validators=[Optional()])
    address_line2 = StringField('Address Line 2', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State/Province', validators=[Optional()])
    postal_code = StringField('Postal Code', validators=[Optional()])
    country = SelectField('Country', choices=[
        ('', 'Select Country'),
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('GB', 'United Kingdom'),
        ('AU', 'Australia'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('IN', 'India'),
        ('BR', 'Brazil'),
        ('RU', 'Russia'),
        ('ZA', 'South Africa')
    ], validators=[Optional()])
    
    # Personal Information
    birthday = DateField('Birthday', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[Optional()])
    marital_status = SelectField('Marital Status', choices=[
        ('', 'Select Status'),
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], validators=[Optional()])
    language = SelectField('Language', choices=[
        ('', 'Select Language'),
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('ru', 'Russian'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean')
    ], validators=[Optional()])
    
    # Social Media
    linkedin = StringField('LinkedIn', validators=[Optional(), URL()])
    twitter = StringField('Twitter', validators=[Optional(), URL()])
    facebook = StringField('Facebook', validators=[Optional(), URL()])
    instagram = StringField('Instagram', validators=[Optional(), URL()])
    github = StringField('GitHub', validators=[Optional(), URL()])
    
    # Professional Information
    department = StringField('Department', validators=[Optional()])
    company_name = StringField('Company Name', validators=[Optional()])
    company_size = SelectField('Company Size', choices=[
        ('', 'Select Size'),
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-200', '51-200'),
        ('201-500', '201-500'),
        ('501-1000', '501-1000'),
        ('1000+', '1000+')
    ], validators=[Optional()])
    industry = StringField('Industry', validators=[Optional()])
    website = StringField('Website', validators=[Optional(), URL()])
    skills = StringField('Skills', validators=[Optional()])
    
    # Additional Information
    bio = TextAreaField('Bio', validators=[Optional()])
    interests = TextAreaField('Interests', validators=[Optional()])
    tags = StringField('Tags', validators=[Optional()])
    
    # Organization
    organization_id = SelectField('Organization', coerce=int, validators=[Optional()])
    
    def populate_obj(self, obj):
        super().populate_obj(obj)
        # Handle empty organization selection
        if self.organization_id.data == 0:
            obj.organization_id = None

class LeadForm(FlaskForm):
    # Contact Information (from ContactForm)
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    title = StringField('Job Title', validators=[Optional()])
    
    # Social Media Links
    linkedin = StringField('LinkedIn', validators=[Optional(), URL()])
    twitter = StringField('Twitter', validators=[Optional(), URL()])
    facebook = StringField('Facebook', validators=[Optional(), URL()])
    instagram = StringField('Instagram', validators=[Optional(), URL()])
    github = StringField('GitHub', validators=[Optional(), URL()])
    
    # Organization
    organization_id = SelectField('Organization', coerce=int, validators=[DataRequired()])
    
    # Lead Details
    source = SelectField('Source', choices=[
        ('', 'Select Source'),
        ('Website', 'Website'),
        ('Referral', 'Referral'),
        ('Social Media', 'Social Media'),
        ('Email Campaign', 'Email Campaign'),
        ('Other', 'Other')
    ])
    source_origin = StringField('Source Origin', validators=[Optional()])
    source_channel = StringField('Source Channel', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('qualified', 'Qualified/Meeting'),
        ('poc', 'PoC/Site Visit'),
        ('proposal', 'Proposal'),
        ('quotation', 'Quotation'),
        ('negotiations', 'Negotiations')
    ])
    deal_value = StringField('Deal Value', validators=[Optional()])
    probability = IntegerField('Probability', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    interested_in = TextAreaField('Interested In', validators=[Optional()])
    requirements = TextAreaField('Requirements', validators=[Optional()])
    budget = StringField('Budget', validators=[Optional()])
    next_follow_up = DateField('Next Follow-up', validators=[Optional()])

class CustomerForm(FlaskForm):
    # Contact Information (from ContactForm)
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    title = StringField('Job Title', validators=[Optional()])
    
    # Organization
    organization_id = SelectField('Organization', coerce=int, validators=[Optional()])
    
    # Customer Details
    company_name = StringField('Company Name', validators=[Optional()])
    industry = StringField('Industry', validators=[Optional()])
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
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending')
    ])
    notes = TextAreaField('Notes', validators=[Optional()])

class InteractionForm(FlaskForm):
    contact_id = HiddenField('Contact ID', validators=[DataRequired()])
    type = SelectField('Type', choices=[], validators=[DataRequired()])
    
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()])
    
    description = TextAreaField('Description')
    notes = TextAreaField('Notes')
    location = StringField('Location', validators=[Length(max=255)])
    
    start_date = DateField('Start Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_date = DateField('End Date')
    end_time = TimeField('End Time')
    
    status = SelectField('Status', choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled')
    ], validators=[DataRequired()])
    
    outcome = TextAreaField('Outcome')
    next_steps = TextAreaField('Next Steps')
    assigned_to_id = SelectField('Assign To', coerce=int, choices=[])
    
    submit = SubmitField('Save Interaction')

    def __init__(self, *args, **kwargs):
        super(InteractionForm, self).__init__(*args, **kwargs)
        from app.models import Interaction, User
        self.type.choices = [(k, v) for k, v in Interaction.TYPE_CHOICES.items()]
        self.priority.choices = [(k, v) for k, v in Interaction.PRIORITY_CHOICES.items()]
        self.status.choices = [(k, v) for k, v in Interaction.STATUS_CHOICES.items()]
        self.assigned_to_id.choices = [(user.id, f"{user.first_name} {user.last_name}") for user in User.query.all()]

class OrganizationForm(FlaskForm):
    # Basic Information (Normal Flow)
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    industry = SelectField('Industry', choices=[], validators=[Optional()])
    website = StringField('Website', validators=[Optional(), URL()])
    status = SelectField('Status', choices=[], validators=[Optional()])
    
    # Company Details (Normal Flow)
    size = SelectField('Company Size', choices=[], validators=[Optional()])
    annual_revenue = FloatField('Annual Revenue', validators=[Optional()])
    founded_year = IntegerField('Founded Year', validators=[Optional()])
    
    # Contact Information (Normal Flow)
    primary_email = StringField('Primary Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    
    # Address Information (Normal Flow)
    address_line1 = StringField('Address Line 1', validators=[Optional()])
    address_line2 = StringField('Address Line 2', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State/Province', validators=[Optional()])
    postal_code = StringField('Postal Code', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])
    
    # Additional Information (Normal Flow)
    segment_tags = StringField('Segment Tags', validators=[Optional()])
    custom_fields = TextAreaField('Custom Fields', validators=[Optional()])
    
    # AI-Driven Fields (read-only, populated by AI)
    clv = FloatField('Customer Lifetime Value', render_kw={'readonly': True})
    engagement_score = IntegerField('Engagement Score', render_kw={'readonly': True})
    churn_risk = FloatField('Churn Risk', render_kw={'readonly': True})
    upsell_potential = StringField('Upsell Potential', render_kw={'readonly': True})
    next_best_action = StringField('Next Best Action', render_kw={'readonly': True})
    
    submit = SubmitField('Save Organization')
    
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        from app.models import Organization
        self.industry.choices = [(k, v) for k, v in Organization.INDUSTRY_CHOICES.items()]
        self.size.choices = [(k, v) for k, v in Organization.SIZE_CHOICES.items()]
        self.status.choices = [(k, v) for k, v in Organization.STATUS_CHOICES.items()]

class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password')
    role_id = SelectField('Role', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Active')
    is_approved = BooleanField('Approved Account')
    submit = SubmitField('Save User')

    def __init__(self, *args, **kwargs):
        self.is_create = kwargs.pop('is_create', False)
        super().__init__(*args, **kwargs)

    def validate(self, extra_validators=None):
        rv = super().validate(extra_validators=extra_validators)
        if not rv:
            return False
        # Only require password match if creating or if confirm_password is filled
        if self.is_create or self.confirm_password.data:
            if self.password.data != self.confirm_password.data:
                self.confirm_password.errors.append('Passwords must match')
                return False
        return True

class RoleForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    permissions = SelectMultipleField('Permissions', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Role') 