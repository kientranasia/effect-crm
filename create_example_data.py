from flask import Flask
from app import create_app, db
from app.models import Organization, Lead, Customer, User, Role
from faker import Faker
from datetime import datetime, timedelta
import random

def create_example_data():
    print("Starting example data creation...")
    
    app = create_app()
    with app.app_context():
        print("Checking database connection...")
        try:
            # Ensure tables exist
            db.create_all()
            
            # Get or create admin user
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                print("Admin user not found!")
                return
                
            print(f"Found admin user: {admin.email}")
            
            # Create organizations
            fake = Faker()
            industries = ['Technology', 'Healthcare', 'Finance', 'Education', 'Manufacturing']
            sizes = ['Small', 'Medium', 'Large', 'Enterprise']
            
            print("Creating organizations...")
            for i in range(20):
                org = Organization(
                    name=fake.company(),
                    description=fake.catch_phrase(),
                    industry=random.choice(industries),
                    website=f"https://{fake.domain_name()}",
                    status='Active',
                    created_at=datetime.utcnow()
                )
                db.session.add(org)
            db.session.commit()
            print("Created 20 organizations")
            
            # Create leads
            print("Creating leads...")
            organizations = Organization.query.all()
            statuses = ['New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation']
            sources = ['Website', 'Referral', 'LinkedIn', 'Conference', 'Cold Call']
            
            for i in range(40):
                org = random.choice(organizations)
                status = random.choice(statuses)
                created_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
                
                lead = Lead(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    phone=fake.phone_number(),
                    job_title=fake.job(),
                    company_name=fake.company(),
                    industry=random.choice(industries),
                    company_size=random.choice(sizes),
                    website=f"https://{fake.domain_name()}",
                    source=random.choice(sources),
                    status=status,
                    notes=fake.text(),
                    created_at=created_date,
                    assigned_to_id=admin.id,
                    organization_id=org.id
                )
                db.session.add(lead)
            db.session.commit()
            print("Created 40 leads")
            
            # Convert first 10 leads to customers
            print("Converting leads to customers...")
            leads_to_convert = Lead.query.limit(10).all()
            for lead in leads_to_convert:
                customer = Customer(
                    first_name=lead.first_name,
                    last_name=lead.last_name,
                    email=lead.email,
                    phone=lead.phone,
                    job_title=lead.job_title,
                    company_name=lead.company_name,
                    industry=lead.industry,
                    company_size=lead.company_size,
                    website=lead.website,
                    status='Active',
                    notes=f"Converted from lead. {lead.notes}",
                    assigned_to_id=admin.id,
                    organization_id=lead.organization_id,
                    created_at=datetime.utcnow()
                )
                lead.converted = True
                lead.converted_date = datetime.utcnow()
                db.session.add(customer)
            db.session.commit()
            print("Converted 10 leads to customers")
            
            # Print summary
            print("\nExample data creation completed!")
            print(f"Created organizations: {Organization.query.count()}")
            print(f"Created leads: {Lead.query.count()}")
            print(f"Created customers: {Customer.query.count()}")
            
        except Exception as e:
            print(f"Error creating example data: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_example_data() 