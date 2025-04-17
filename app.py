# app.py - Main Flask application
from app import create_app, db
from app.models import User, Customer, Interaction
import os
from datetime import datetime
import anthropic
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the Flask application
app = create_app()

# Set up API keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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

# Demo analysis function for testing
def get_demo_analysis(text, analysis_type="general"):
    """Return a demo analysis for testing purposes"""
    if analysis_type == "sentiment":
        return """
        <h3>Sentiment Analysis</h3>
        <p><strong>Overall Sentiment:</strong> Positive</p>
        <p><strong>Emotional Tone:</strong> Enthusiastic and interested</p>
        <p><strong>Key Indicators:</strong></p>
        <ul>
            <li>Use of positive language: "excited", "impressed", "looking forward"</li>
            <li>Engagement level: High (asking detailed questions)</li>
            <li>Decision-making signals: Mentioning timeline and budget</li>
        </ul>
        <p><strong>Recommendation:</strong> The customer is showing strong interest. Prioritize follow-up with specific product information and pricing details.</p>
        """
    elif analysis_type == "actionable":
        return """
        <h3>Actionable Insights</h3>
        <p><strong>Priority Actions:</strong></p>
        <ol>
            <li><strong>Schedule a product demo</strong> - The customer expressed interest in seeing the product in action. This should be done within 48 hours.</li>
            <li><strong>Prepare pricing proposal</strong> - The customer mentioned budget constraints. A tailored pricing proposal would address this concern.</li>
            <li><strong>Research competitor mentioned</strong> - The customer compared your solution to a competitor. Gather information to highlight your advantages.</li>
        </ol>
        <p><strong>Timeline:</strong> The customer mentioned a decision by end of quarter, suggesting a 2-3 week window for closing.</p>
        """
    elif analysis_type == "summary":
        return """
        <h3>Executive Summary</h3>
        <p><strong>Business Impact:</strong> Medium to High - The customer represents a potential $50,000 annual contract.</p>
        <p><strong>Decision Timeline:</strong> End of current quarter (approximately 3 weeks)</p>
        <p><strong>Deal Potential:</strong> 70% - The customer has a clear need, budget, and timeline, but is evaluating multiple options.</p>
        <p><strong>Key Stakeholders:</strong> The primary contact is the IT Director, but final approval will come from the CFO.</p>
        <p><strong>Next Steps:</strong> Schedule a technical demo and prepare a competitive pricing proposal.</p>
        """
    else:  # general is the default
        return """
        <h3>Interaction Analysis</h3>
        <p><strong>Key Insights:</strong></p>
        <ul>
            <li>The customer is actively looking to replace their current solution within the next quarter</li>
            <li>Budget is a concern, but not a blocker</li>
            <li>They are evaluating multiple vendors, including a specific competitor</li>
            <li>The IT Director is the primary decision maker, but CFO approval is required</li>
        </ul>
        <p><strong>Sentiment:</strong> Positive - The customer is engaged and asking detailed questions</p>
        <p><strong>Recommended Actions:</strong></p>
        <ol>
            <li>Schedule a product demo within the next week</li>
            <li>Prepare a competitive pricing proposal</li>
            <li>Research the competitor mentioned to highlight your advantages</li>
            <li>Follow up with case studies from similar industries</li>
        </ol>
        """

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))

# Add other routes as needed

if __name__ == '__main__':
    app.run(debug=True)