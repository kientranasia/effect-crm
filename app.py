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
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', customers=customers)

@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        status = request.form.get('status')
        
        new_customer = Customer(
            name=name,
            email=email,
            phone=phone,
            status=status,
            user_id=current_user.id
        )
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added successfully', 'success')
    
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    return render_template('customers.html', customers=customers)

@app.route('/customer/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers'))
    
    interactions = Interaction.query.filter_by(customer_id=customer_id).order_by(Interaction.timestamp.desc()).all()
    return render_template('customer_detail.html', customer=customer, interactions=interactions)

@app.route('/customer/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers'))
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        customer.status = request.form.get('status')
        customer.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customer_detail', customer_id=customer.id))
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers'))
    
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully', 'success')
    return redirect(url_for('customers'))

@app.route('/customer/<int:customer_id>/add_interaction', methods=['GET', 'POST'])
@login_required
def add_interaction(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers'))
    
    if request.method == 'POST':
        interaction_type = request.form.get('type')
        summary = request.form.get('summary')
        details = request.form.get('details')
        llm_provider = request.form.get('llm_provider')
        analysis_type = request.form.get('analysis_type', 'general')
        
        new_interaction = Interaction(
            type=interaction_type,
            summary=summary,
            details=details,
            customer_id=customer_id
        )
        
        # Update customer's last contact time
        customer.last_contact = datetime.utcnow()
        
        # Process with LLM if selected
        if llm_provider:
            text_to_analyze = f"Customer: {customer.name}\nInteraction Type: {interaction_type}\nSummary: {summary}\nDetails: {details}"
            
            if llm_provider == 'claude':
                analysis = analyze_with_claude(text_to_analyze, analysis_type)
            elif llm_provider == 'openai':
                analysis = analyze_with_openai(text_to_analyze, analysis_type)
            elif llm_provider == 'demo':
                analysis = get_demo_analysis(text_to_analyze, analysis_type)
            else:
                analysis = "No LLM analysis requested"
                
            new_interaction.ai_analysis = analysis
        
        db.session.add(new_interaction)
        db.session.commit()
        flash('Interaction added successfully', 'success')
        return redirect(url_for('customer_detail', customer_id=customer.id))
    
    return render_template('add_interaction.html', customer=customer)

# Add a new route to analyze an existing interaction
@app.route('/interaction/<int:interaction_id>/analyze', methods=['POST'])
@login_required
def analyze_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers'))
    
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
    return redirect(url_for('interaction_detail', interaction_id=interaction.id))


@app.route('/interaction/<int:interaction_id>')
@login_required
def interaction_detail(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('customers'))
    
    return render_template('interaction_detail.html', interaction=interaction, customer=customer)

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