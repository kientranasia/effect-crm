# app.py - Main Flask application
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime
import anthropic
import openai
from dotenv import load_dotenv

import random
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///crm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Set up API keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    customers = db.relationship('Customer', backref='user', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Lead')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_contact = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interactions = db.relationship('Interaction', backref='customer', lazy=True, cascade="all, delete-orphan")
    
    @property
    def last_interaction(self):
        if self.interactions:
            return max(self.interactions, key=lambda x: x.timestamp)
        return None

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    ai_analysis = db.Column(db.Text)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# LLM Integration Functions
def analyze_with_claude(text, analysis_type="general"):
    """Analyze text using Claude API"""
    if not ANTHROPIC_API_KEY:
        return "<p>API key not configured. Please add your Anthropic API key to the .env file.</p>"
    
    try:
        # Create a prompt based on the analysis type
        system_prompt = "You are a helpful CRM assistant that analyzes customer interactions and provides insights."
        user_prompt = f"Analyze this customer interaction and provide "
        
        if analysis_type == "sentiment":
            user_prompt += "a detailed sentiment analysis with emotional tone detection and specific language indicators."
        elif analysis_type == "actionable":
            user_prompt += "specific actionable next steps ranked by priority, with clear justifications for each recommendation."
        elif analysis_type == "summary":
            user_prompt += "an executive summary focused on business impact, decision timeline, and deal potential."
        else:  # general is the default
            user_prompt += "key insights, sentiment, and recommended follow-up actions."
            
        user_prompt += f" Format your response in HTML for better readability: {text}"
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"<p>Error with Claude API: {str(e)}</p>"

# Modify the analyze_with_openai function similarly
def analyze_with_openai(text, analysis_type="general"):
    """Analyze text using OpenAI API"""
    if not OPENAI_API_KEY:
        return "<p>API key not configured. Please add your OpenAI API key to the .env file.</p>"
    
    try:
        # Create a prompt based on the analysis type
        system_prompt = "You are a helpful CRM assistant that analyzes customer interactions and provides insights."
        user_prompt = f"Analyze this customer interaction and provide "
        
        if analysis_type == "sentiment":
            user_prompt += "a detailed sentiment analysis with emotional tone detection and specific language indicators."
        elif analysis_type == "actionable":
            user_prompt += "specific actionable next steps ranked by priority, with clear justifications for each recommendation."
        elif analysis_type == "summary":
            user_prompt += "an executive summary focused on business impact, decision timeline, and deal potential."
        else:  # general is the default
            user_prompt += "key insights, sentiment, and recommended follow-up actions."
            
        user_prompt += f" Format your response in HTML for better readability: {text}"
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"<p>Error with OpenAI API: {str(e)}</p>"

# Add this new function to provide demo analysis when no API keys are available
def get_demo_analysis(text, analysis_type="general"):
    """Generate demo analysis without requiring API keys"""
    customer_name = 'this customer'
    if 'Customer:' in text and '\n' in text:
        customer_name = text.split('Customer:')[1].split('\n')[0].strip()
    
    general_responses = [
        f"""<h5>Analysis Summary</h5>
        <p>The interaction with {customer_name} appears to be positive overall. The customer expressed interest in our product offerings and has requested additional information.</p>
        
        <h5>Key Insights</h5>
        <ul>
            <li>Customer is in the research phase of their buying journey</li>
            <li>Price sensitivity was mentioned twice during the conversation</li>
            <li>Customer mentioned a competitor's product, indicating they're exploring alternatives</li>
        </ul>
        
        <h5>Recommended Follow-up</h5>
        <p>Schedule a follow-up call in 5-7 days to discuss any questions after they've reviewed the information. Consider preparing a competitive comparison highlighting our unique value proposition.</p>""",
        
        f"""<h5>Interaction Analysis</h5>
        <p>This was a somewhat neutral interaction with {customer_name}. The customer had several technical questions about implementation that suggest they're evaluating feasibility.</p>
        
        <h5>Key Points</h5>
        <ul>
            <li>Customer has existing infrastructure they need to integrate with</li>
            <li>Timeline concerns were mentioned multiple times</li>
            <li>Customer's technical team will need to be involved in future discussions</li>
        </ul>
        
        <h5>Suggested Actions</h5>
        <p>Arrange a technical demonstration with their IT department. Prepare documentation addressing the specific integration points they mentioned.</p>"""
    ]
    
    sentiment_responses = [
        f"""<h5>Sentiment Analysis</h5>
        <div class="progress mb-3">
            <div class="progress-bar bg-success" role="progressbar" style="width: 78%" aria-valuenow="78" aria-valuemin="0" aria-valuemax="100">78% Positive</div>
        </div>
        
        <h5>Emotional Tone Detection</h5>
        <ul>
            <li><strong>Interest:</strong> High</li>
            <li><strong>Satisfaction:</strong> Moderate</li>
            <li><strong>Concerns:</strong> Low</li>
        </ul>
        
        <p>The customer's language indicates a generally positive attitude toward our offering, with specific enthusiasm about the features discussed. There are minor concerns about implementation timeline that should be addressed.</p>""",
        
        f"""<h5>Sentiment Analysis</h5>
        <div class="progress mb-3">
            <div class="progress-bar bg-warning" role="progressbar" style="width: 45%" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100">45% Positive</div>
        </div>
        
        <h5>Emotional Tone Detection</h5>
        <ul>
            <li><strong>Interest:</strong> Moderate</li>
            <li><strong>Satisfaction:</strong> Low</li>
            <li><strong>Concerns:</strong> High</li>
        </ul>
        
        <p>The customer's communication shows some reservation. They asked multiple questions about reliability and support, suggesting previous negative experiences. Address these concerns directly in follow-up communications.</p>"""
    ]
    
    actionable_responses = [
        f"""<h5>Actionable Insights</h5>
        <ol>
            <li><strong>Send Feature Comparison Document</strong><br>Customer specifically asked for comparison with competitors.</li>
            <li><strong>Schedule Technical Demo</strong><br>Focus on integration capabilities they expressed concerns about.</li>
            <li><strong>Prepare Custom Pricing Proposal</strong><br>Address budget concerns with tailored package.</li>
            <li><strong>Connect with Decision Maker</strong><br>Current contact indicated final decision rests with their manager.</li>
        </ol>
        
        <h5>Priority Level</h5>
        <span class="badge bg-success">HIGH PRIORITY</span>
        <p class="mt-2">This opportunity has high conversion potential if we address technical concerns quickly.</p>""",
        
        f"""<h5>Actionable Insights</h5>
        <ol>
            <li><strong>Provide Case Studies</strong><br>Customer requested examples from similar companies in their industry.</li>
            <li><strong>Follow Up in 2 Weeks</strong><br>They mentioned their review process takes approximately 10 business days.</li>
            <li><strong>Include Support Team in Next Call</strong><br>Customer had detailed questions about support processes.</li>
        </ol>
        
        <h5>Priority Level</h5>
        <span class="badge bg-warning">MEDIUM PRIORITY</span>
        <p class="mt-2">Customer is still in early evaluation stage but showing genuine interest.</p>"""
    ]
    
    summary_responses = [
        f"""<h5>Executive Summary</h5>
        <p>Initial contact with {customer_name} indicates a promising opportunity. They have immediate needs that align with our core offerings, particularly in the areas of reporting and data integration.</p>
        
        <h5>Key Takeaways</h5>
        <ul>
            <li>Decision timeline: 30 days</li>
            <li>Budget: Aligned with our Enterprise tier</li>
            <li>Main driver: Improving operational efficiency</li>
            <li>Potential deal size: Medium to Large</li>
        </ul>
        
        <h5>Next Steps</h5>
        <p>Recommend moving forward with a tailored demonstration focused on their specific use case. Sales engineer involvement recommended for next meeting.</p>""",
        
        f"""<h5>Executive Summary</h5>
        <p>Exploratory discussion with {customer_name} revealed potential fit for our Standard package. Customer is comparing multiple solutions and has expressed price sensitivity.</p>
        
        <h5>Key Takeaways</h5>
        <ul>
            <li>Decision timeline: 60-90 days</li>
            <li>Budget: Limited, seeking value option</li>
            <li>Main driver: Regulatory compliance requirements</li>
            <li>Potential deal size: Small to Medium</li>
        </ul>
        
        <h5>Next Steps</h5>
        <p>Recommend providing detailed feature comparison highlighting our compliance capabilities. Consider offering limited-time discount to accelerate decision process.</p>"""
    ]
    
    if analysis_type == "sentiment":
        return random.choice(sentiment_responses)
    elif analysis_type == "actionable":
        return random.choice(actionable_responses)
    elif analysis_type == "summary":
        return random.choice(summary_responses)
    else:  # general is the default
        return random.choice(general_responses)
    

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # In a real app, use proper password hashing
        if user and user.password == password:
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        # In a real app, hash the password
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get all customers for the current user
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    
    # Calculate customer statistics
    total_customers = len(customers)
    active_customers = sum(1 for c in customers if c.status == 'Active')
    lead_customers = sum(1 for c in customers if c.status == 'Lead')
    lost_customers = sum(1 for c in customers if c.status == 'Lost')
    
    # Get recent customers (last 5)
    recent_customers = Customer.query.filter_by(user_id=current_user.id).order_by(Customer.created_at.desc()).limit(5).all()
    
    # Get all interactions for the current user's customers
    customer_ids = [c.id for c in customers]
    recent_interactions = Interaction.query.filter(Interaction.customer_id.in_(customer_ids)).order_by(Interaction.timestamp.desc()).limit(5).all()
    
    # Get customer status distribution
    status_distribution = {}
    for customer in customers:
        status = customer.status
        if status in status_distribution:
            status_distribution[status] += 1
        else:
            status_distribution[status] = 1
    
    # Get interactions by type
    interaction_types = {}
    for interaction in Interaction.query.filter(Interaction.customer_id.in_(customer_ids)).all():
        interaction_type = interaction.type
        if interaction_type in interaction_types:
            interaction_types[interaction_type] += 1
        else:
            interaction_types[interaction_type] = 1
    
    # Get customers by month (for chart)
    from collections import defaultdict
    customers_by_month = defaultdict(int)
    for customer in customers:
        month = customer.created_at.strftime('%Y-%m')
        customers_by_month[month] += 1
    
    # Sort months chronologically
    sorted_months = sorted(customers_by_month.keys())
    
    return render_template('dashboard.html', 
                          customers=customers,
                          total_customers=total_customers,
                          active_customers=active_customers,
                          lead_customers=lead_customers,
                          lost_customers=lost_customers,
                          recent_customers=recent_customers,
                          recent_interactions=recent_interactions,
                          status_distribution=status_distribution,
                          interaction_types=interaction_types,
                          customers_by_month=customers_by_month,
                          sorted_months=sorted_months)

# Customer routes
@app.route('/customers')
@login_required
def customers_show():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'name')
    
    # Base query
    query = Customer.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(Customer.name.ilike(f'%{search}%') | Customer.email.ilike(f'%{search}%'))
    if status:
        query = query.filter_by(status=status)
    
    # Apply sorting
    if sort == 'name':
        query = query.order_by(Customer.name)
    elif sort == 'created_at':
        query = query.order_by(Customer.created_at.desc())
    elif sort == 'status':
        query = query.order_by(Customer.status)
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page)
    customers = pagination.items
    
    return render_template('customers/index.html', customers=customers, pagination=pagination)

@app.route('/customers/create', methods=['GET', 'POST'])
@login_required
def customers_create():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        company = request.form.get('company')
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        new_customer = Customer(
            name=name,
            email=email,
            phone=phone,
            status=status,
            notes=notes,
            user_id=current_user.id
        )
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added successfully', 'success')
        return redirect(url_for('customers_show'))
    
    return render_template('customers/form.html')

@app.route('/customers/<int:customer_id>')
@login_required
def customers_detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers_show'))
    
    interactions = Interaction.query.filter_by(customer_id=customer_id).order_by(Interaction.timestamp.desc()).all()
    return render_template('customers/detail.html', customer=customer, interactions=interactions)

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def customers_edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers_show'))
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        customer.company = request.form.get('company')
        customer.status = request.form.get('status')
        customer.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customers_detail', customer_id=customer.id))
    
    return render_template('customers/form.html', customer=customer)

@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def customers_delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers_show'))
    
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully', 'success')
    return redirect(url_for('customers_show'))

# Interaction routes
@app.route('/interactions')
@login_required
def interactions_show():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    search = request.args.get('search', '')
    interaction_type = request.args.get('type', '')
    customer_id = request.args.get('customer_id', type=int)
    
    # Base query - get interactions for all customers of the current user
    customer_ids = [c.id for c in Customer.query.filter_by(user_id=current_user.id).all()]
    query = Interaction.query.filter(Interaction.customer_id.in_(customer_ids))
    
    # Apply filters
    if search:
        query = query.filter(Interaction.summary.ilike(f'%{search}%'))
    if interaction_type:
        query = query.filter_by(type=interaction_type)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    # Sort by timestamp (newest first)
    query = query.order_by(Interaction.timestamp.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page)
    interactions = pagination.items
    
    # Get all customers for the filter dropdown
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    
    return render_template('interactions/index.html', interactions=interactions, customers=customers, pagination=pagination)

@app.route('/interactions/create', methods=['GET', 'POST'])
@login_required
def interactions_create():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        interaction_type = request.form.get('type')
        summary = request.form.get('summary')
        details = request.form.get('details')
        timestamp = datetime.strptime(request.form.get('timestamp'), '%Y-%m-%dT%H:%M')
        
        # Verify customer belongs to current user
        customer = Customer.query.get_or_404(customer_id)
        if customer.user_id != current_user.id:
            flash('Unauthorized access', 'error')
            return redirect(url_for('interactions_show'))
        
        new_interaction = Interaction(
            type=interaction_type,
            summary=summary,
            details=details,
            timestamp=timestamp,
            customer_id=customer_id
        )
        
        db.session.add(new_interaction)
        db.session.commit()
        flash('Interaction added successfully', 'success')
        return redirect(url_for('interactions_detail', interaction_id=new_interaction.id))
    
    # Get all customers for the dropdown
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    return render_template('interactions/form.html', customers=customers)

@app.route('/interactions/<int:interaction_id>')
@login_required
def interactions_detail(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions_show'))
    
    return render_template('interaction_detail.html', interaction=interaction, customer=customer)

@app.route('/interactions/<int:interaction_id>/edit', methods=['GET', 'POST'])
@login_required
def interactions_edit(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions_show'))
    
    if request.method == 'POST':
        interaction.type = request.form.get('type')
        interaction.summary = request.form.get('summary')
        interaction.details = request.form.get('details')
        interaction.timestamp = datetime.strptime(request.form.get('timestamp'), '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        flash('Interaction updated successfully', 'success')
        return redirect(url_for('interactions_detail', interaction_id=interaction.id))
    
    return render_template('interactions/form.html', interaction=interaction)

@app.route('/interactions/<int:interaction_id>/delete', methods=['POST'])
@login_required
def interactions_delete(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions_show'))
    
    db.session.delete(interaction)
    db.session.commit()
    flash('Interaction deleted successfully', 'success')
    return redirect(url_for('interactions_show'))

@app.route('/interactions/<int:interaction_id>/analyze', methods=['POST'])
@login_required
def interactions_analyze(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions_show'))
    
    llm_provider = request.form.get('llm_provider')
    analysis_type = request.form.get('analysis_type', 'general')
    
    text_to_analyze = f"Customer: {customer.name}\nInteraction Type: {interaction.type}\nSummary: {interaction.summary}\nDetails: {interaction.details}"
    
    if llm_provider == 'claude':
        analysis = analyze_with_claude(text_to_analyze, analysis_type)
    elif llm_provider == 'openai':
        analysis = analyze_with_openai(text_to_analyze, analysis_type)
    elif llm_provider == 'demo':
        analysis = get_demo_analysis(text_to_analyze, analysis_type)
    else:
        analysis = "No analysis was generated"
    
    interaction.ai_analysis = analysis
    db.session.commit()
    
    flash('Analysis generated successfully', 'success')
    return redirect(url_for('interactions_detail', interaction_id=interaction.id))

@app.route('/api/analyze_with_llm', methods=['POST'])
@login_required
def api_analyze_with_llm():
    data = request.json
    text = data.get('text', '')
    provider = data.get('provider', 'claude')
    
    if provider == 'claude':
        analysis = analyze_with_claude(text)
    else:
        analysis = analyze_with_openai(text)
    
    return jsonify({"analysis": analysis})

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)