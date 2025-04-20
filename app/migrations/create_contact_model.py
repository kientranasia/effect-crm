from app import db
from app.models.contact import Contact
from app.models import Lead, Customer, Organization, User
from datetime import datetime

def upgrade():
    """Create the contacts table and migrate data from leads and customers"""
    # Create the contacts table
    db.session.execute("""
    CREATE TABLE contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(64) NOT NULL,
        last_name VARCHAR(64) NOT NULL,
        email VARCHAR(120) NOT NULL,
        phone VARCHAR(20),
        job_title VARCHAR(100),
        organization_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        -- Enhanced fields for better LLM support and CRM functionality
        -- Personal information
        middle_name VARCHAR(64),
        nickname VARCHAR(64),
        birthday DATE,
        gender VARCHAR(20),
        marital_status VARCHAR(20),
        language VARCHAR(10),
        
        -- Contact information
        mobile_phone VARCHAR(20),
        work_phone VARCHAR(20),
        home_phone VARCHAR(20),
        fax VARCHAR(20),
        alternate_email VARCHAR(120),
        
        -- Social media
        linkedin VARCHAR(200),
        twitter VARCHAR(200),
        facebook VARCHAR(200),
        instagram VARCHAR(200),
        github VARCHAR(200),
        
        -- Location
        address_line1 VARCHAR(200),
        address_line2 VARCHAR(200),
        city VARCHAR(100),
        state VARCHAR(100),
        postal_code VARCHAR(20),
        country VARCHAR(100),
        
        -- Professional information
        department VARCHAR(100),
        company_name VARCHAR(100),
        company_size VARCHAR(50),
        industry VARCHAR(100),
        website VARCHAR(200),
        
        -- Additional metadata for LLM support
        bio TEXT,
        interests TEXT,
        skills TEXT,
        education TEXT,
        work_history TEXT,
        preferences TEXT,
        tags VARCHAR(500),
        custom_fields TEXT,
        
        FOREIGN KEY (organization_id) REFERENCES organizations (id)
    )
    """)
    
    # Add contact_id column to leads table
    db.session.execute("""
    ALTER TABLE leads ADD COLUMN contact_id INTEGER
    """)
    
    # Add contact_id column to customers table
    db.session.execute("""
    ALTER TABLE customers ADD COLUMN contact_id INTEGER
    """)
    
    # Migrate data from leads to contacts
    leads = db.session.execute("SELECT * FROM leads").fetchall()
    for lead in leads:
        # Create a contact for each lead
        contact = Contact(
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            job_title=lead.job_title,
            organization_id=lead.organization_id,
            created_at=lead.created_at
        )
        db.session.add(contact)
        db.session.flush()  # Get the contact ID without committing
        
        # Update the lead with the new contact_id
        db.session.execute(
            "UPDATE leads SET contact_id = ? WHERE id = ?",
            (contact.id, lead.id)
        )
    
    # Migrate data from customers to contacts
    customers = db.session.execute("SELECT * FROM customers").fetchall()
    for customer in customers:
        # Check if a contact with the same email already exists
        existing_contact = db.session.execute(
            "SELECT id FROM contacts WHERE email = ?",
            (customer.email,)
        ).fetchone()
        
        if existing_contact:
            # Use the existing contact
            contact_id = existing_contact.id
        else:
            # Create a new contact
            contact = Contact(
                first_name=customer.first_name,
                last_name=customer.last_name,
                email=customer.email,
                phone=customer.phone,
                job_title=customer.job_title,
                organization_id=customer.organization_id,
                created_at=customer.created_at
            )
            db.session.add(contact)
            db.session.flush()  # Get the contact ID without committing
            contact_id = contact.id
        
        # Update the customer with the new contact_id
        db.session.execute(
            "UPDATE customers SET contact_id = ? WHERE id = ?",
            (contact_id, customer.id)
        )
    
    # Add foreign key constraints
    db.session.execute("""
    ALTER TABLE leads ADD CONSTRAINT fk_leads_contact
    FOREIGN KEY (contact_id) REFERENCES contacts (id)
    """)
    
    db.session.execute("""
    ALTER TABLE customers ADD CONSTRAINT fk_customers_contact
    FOREIGN KEY (contact_id) REFERENCES contacts (id)
    """)
    
    # Drop the old columns from leads and customers
    db.session.execute("""
    ALTER TABLE leads DROP COLUMN first_name;
    ALTER TABLE leads DROP COLUMN last_name;
    ALTER TABLE leads DROP COLUMN email;
    ALTER TABLE leads DROP COLUMN phone;
    ALTER TABLE leads DROP COLUMN job_title;
    ALTER TABLE leads DROP COLUMN organization_id;
    """)
    
    db.session.execute("""
    ALTER TABLE customers DROP COLUMN first_name;
    ALTER TABLE customers DROP COLUMN last_name;
    ALTER TABLE customers DROP COLUMN email;
    ALTER TABLE customers DROP COLUMN phone;
    ALTER TABLE customers DROP COLUMN job_title;
    ALTER TABLE customers DROP COLUMN organization_id;
    """)
    
    db.session.commit()

def downgrade():
    """Revert the changes made in the upgrade function"""
    # Add back the old columns to leads
    db.session.execute("""
    ALTER TABLE leads ADD COLUMN first_name VARCHAR(64);
    ALTER TABLE leads ADD COLUMN last_name VARCHAR(64);
    ALTER TABLE leads ADD COLUMN email VARCHAR(120);
    ALTER TABLE leads ADD COLUMN phone VARCHAR(20);
    ALTER TABLE leads ADD COLUMN job_title VARCHAR(100);
    ALTER TABLE leads ADD COLUMN organization_id INTEGER;
    """)
    
    # Add back the old columns to customers
    db.session.execute("""
    ALTER TABLE customers ADD COLUMN first_name VARCHAR(64);
    ALTER TABLE customers ADD COLUMN last_name VARCHAR(64);
    ALTER TABLE customers ADD COLUMN email VARCHAR(120);
    ALTER TABLE customers ADD COLUMN phone VARCHAR(20);
    ALTER TABLE customers ADD COLUMN job_title VARCHAR(100);
    ALTER TABLE customers ADD COLUMN organization_id INTEGER;
    """)
    
    # Migrate data back from contacts to leads
    leads = db.session.execute("SELECT * FROM leads").fetchall()
    for lead in leads:
        contact = db.session.execute(
            "SELECT * FROM contacts WHERE id = ?",
            (lead.contact_id,)
        ).fetchone()
        
        if contact:
            db.session.execute(
                """
                UPDATE leads 
                SET first_name = ?, last_name = ?, email = ?, phone = ?, 
                    job_title = ?, organization_id = ?
                WHERE id = ?
                """,
                (contact.first_name, contact.last_name, contact.email, 
                 contact.phone, contact.job_title, contact.organization_id, lead.id)
            )
    
    # Migrate data back from contacts to customers
    customers = db.session.execute("SELECT * FROM customers").fetchall()
    for customer in customers:
        contact = db.session.execute(
            "SELECT * FROM contacts WHERE id = ?",
            (customer.contact_id,)
        ).fetchone()
        
        if contact:
            db.session.execute(
                """
                UPDATE customers 
                SET first_name = ?, last_name = ?, email = ?, phone = ?, 
                    job_title = ?, organization_id = ?
                WHERE id = ?
                """,
                (contact.first_name, contact.last_name, contact.email, 
                 contact.phone, contact.job_title, contact.organization_id, customer.id)
            )
    
    # Drop the contact_id columns and foreign key constraints
    db.session.execute("""
    ALTER TABLE leads DROP COLUMN contact_id;
    """)
    
    db.session.execute("""
    ALTER TABLE customers DROP COLUMN contact_id;
    """)
    
    # Drop the contacts table
    db.session.execute("DROP TABLE contacts")
    
    db.session.commit() 