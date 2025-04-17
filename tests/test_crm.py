import unittest
import os
import tempfile
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.organization import Organization
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.interaction import Interaction
from app.models.workspace import Workspace, workspace_users
from config import TestingConfig

class CRMTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app(TestingConfig)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Create application context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create database tables
        db.create_all()
        
        # Create admin role
        admin_role = Role(name='admin', description='Administrator with full access')
        db.session.add(admin_role)
        db.session.commit()
        
        # Create admin user
        admin_user = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            is_approved=True
        )
        admin_user.set_password('admin123')
        admin_user.role = admin_role
        db.session.add(admin_user)
        db.session.commit()
        
        # Create default organization
        default_org = Organization(
            name='Default Organization',
            description='Default organization for testing',
            industry='Technology',
            website='https://example.com'
        )
        db.session.add(default_org)
        db.session.commit()
        
        # Create default workspace
        default_workspace = Workspace(
            name='Default Workspace',
            description='Default workspace for testing',
            organization_id=default_org.id
        )
        db.session.add(default_workspace)
        db.session.commit()
        
        # Associate admin user with workspace
        db.session.execute(
            workspace_users.insert().values(
                user_id=admin_user.id,
                workspace_id=default_workspace.id
            )
        )
        db.session.commit()
        
        # Store references for later use
        self.admin_user = admin_user
        self.admin_role = admin_role
        self.default_org = default_org
        self.default_workspace = default_workspace
    
    def tearDown(self):
        # Close the database connection and remove the temporary file
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_user_creation(self):
        """Test user creation and properties"""
        # Create a new user
        user = User(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            is_approved=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Test user properties
        self.assertEqual(user.full_name, 'John Doe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertTrue(user.is_approved)
        self.assertFalse(user.is_admin)  # No role assigned yet
        
        # Assign admin role
        user.role = self.admin_role
        db.session.commit()
        self.assertTrue(user.is_admin)
    
    def test_organization_creation(self):
        """Test organization creation and properties"""
        # Create a new organization
        org = Organization(
            name='Test Organization',
            description='Test organization description',
            industry='Finance',
            website='https://testorg.com'
        )
        db.session.add(org)
        db.session.commit()
        
        # Test organization properties
        self.assertEqual(org.name, 'Test Organization')
        self.assertEqual(org.industry, 'Finance')
        self.assertEqual(org.website, 'https://testorg.com')
    
    def test_lead_creation(self):
        """Test lead creation and properties"""
        # Create a new lead
        lead = Lead(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            phone='1234567890',
            job_title='Manager',
            company_name='Smith Corp',
            industry='Healthcare',
            company_size='50-200',
            website='https://smithcorp.com',
            source='Website',
            status='New',
            notes='Test lead notes',
            assigned_to_id=self.admin_user.id,
            organization_id=self.default_org.id
        )
        db.session.add(lead)
        db.session.commit()
        
        # Test lead properties
        self.assertEqual(lead.full_name, 'Jane Smith')
        self.assertEqual(lead.email, 'jane@example.com')
        self.assertEqual(lead.status, 'New')
        self.assertEqual(lead.assigned_to, self.admin_user)
        self.assertEqual(lead.org, self.default_org)
    
    def test_customer_creation(self):
        """Test customer creation and properties"""
        # Create a new customer
        customer = Customer(
            first_name='Robert',
            last_name='Johnson',
            email='robert@example.com',
            phone='9876543210',
            job_title='Director',
            company_name='Johnson Inc',
            industry='Manufacturing',
            company_size='200-500',
            website='https://johnsoninc.com',
            status='Active',
            notes='Test customer notes',
            assigned_to_id=self.admin_user.id,
            organization_id=self.default_org.id
        )
        db.session.add(customer)
        db.session.commit()
        
        # Test customer properties
        self.assertEqual(customer.full_name, 'Robert Johnson')
        self.assertEqual(customer.email, 'robert@example.com')
        self.assertEqual(customer.status, 'Active')
        self.assertEqual(customer.assigned_to, self.admin_user)
    
    def test_interaction_creation(self):
        """Test interaction creation and properties"""
        # Create a customer first
        customer = Customer(
            first_name='Alice',
            last_name='Brown',
            email='alice@example.com',
            status='Active',
            assigned_to_id=self.admin_user.id,
            organization_id=self.default_org.id
        )
        db.session.add(customer)
        db.session.commit()
        
        # Create an interaction
        interaction = Interaction(
            customer_id=customer.id,
            type='Email',
            description='Test interaction',
            date=datetime.now(),
            user_id=self.admin_user.id
        )
        db.session.add(interaction)
        db.session.commit()
        
        # Test interaction properties
        self.assertEqual(interaction.type, 'Email')
        self.assertEqual(interaction.customer, customer)
        self.assertEqual(interaction.user, self.admin_user)
    
    def test_lead_to_customer_conversion(self):
        """Test converting a lead to a customer"""
        # Create a lead
        lead = Lead(
            first_name='Michael',
            last_name='Wilson',
            email='michael@example.com',
            status='New',
            assigned_to_id=self.admin_user.id,
            organization_id=self.default_org.id
        )
        db.session.add(lead)
        db.session.commit()
        
        # Convert lead to customer
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
            notes=lead.notes,
            assigned_to_id=lead.assigned_to_id,
            organization_id=lead.organization_id,
            converted_from_lead_id=lead.id
        )
        db.session.add(customer)
        
        # Update lead status
        lead.status = 'Converted'
        db.session.commit()
        
        # Test conversion
        self.assertEqual(customer.first_name, lead.first_name)
        self.assertEqual(customer.email, lead.email)
        self.assertEqual(lead.status, 'Converted')
    
    def test_authentication(self):
        """Test user authentication"""
        # Test login with correct credentials
        response = self.client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        
        # Test login with incorrect password
        response = self.client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)
        
        # Test login with non-existent user
        response = self.client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)
    
    def test_user_registration(self):
        """Test user registration"""
        # Test registration with valid data
        response = self.client.post('/auth/register', data={
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful! Please wait for admin approval.', response.data)
        
        # Verify user was created in database
        user = User.query.filter_by(email='newuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_approved)  # New users should not be approved by default
        
        # Test registration with existing email
        response = self.client.post('/auth/register', data={
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Email already registered', response.data)
    
    def test_admin_approval(self):
        """Test admin approval of users"""
        # Create a new unapproved user
        user = User(
            first_name='Pending',
            last_name='User',
            email='pending@example.com',
            is_approved=False
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Login as admin
        self.client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'admin123'
        })
        
        # Approve the user
        response = self.client.post(f'/admin/users/approve/{user.id}', follow_redirects=True)
        self.assertIn(f'User {user.email} has been approved.'.encode(), response.data)
        
        # Verify user is now approved
        user = User.query.get(user.id)
        self.assertTrue(user.is_approved)
    
    def test_workspace_association(self):
        """Test workspace and user associations"""
        # Create a new user
        user = User(
            first_name='Workspace',
            last_name='User',
            email='workspace@example.com',
            is_approved=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create a new workspace
        workspace = Workspace(
            name='Test Workspace',
            description='Test workspace description',
            organization_id=self.default_org.id
        )
        db.session.add(workspace)
        db.session.commit()
        
        # Associate user with workspace
        db.session.execute(
            workspace_users.insert().values(
                user_id=user.id,
                workspace_id=workspace.id
            )
        )
        db.session.commit()
        
        # Verify association
        user_workspaces = db.session.query(Workspace).join(
            workspace_users
        ).filter(
            workspace_users.c.user_id == user.id
        ).all()
        
        self.assertEqual(len(user_workspaces), 1)
        self.assertEqual(user_workspaces[0].name, 'Test Workspace')
    
    def test_customer_status_transitions(self):
        """Test customer status transitions"""
        # Create a customer
        customer = Customer(
            first_name='Status',
            last_name='Test',
            email='status@example.com',
            status='Active',
            assigned_to_id=self.admin_user.id,
            organization_id=self.default_org.id
        )
        db.session.add(customer)
        db.session.commit()
        
        # Change status to Lead
        customer.status = 'Lead'
        db.session.commit()
        self.assertEqual(customer.status, 'Lead')
        
        # Change status to Lost
        customer.status = 'Lost'
        db.session.commit()
        self.assertEqual(customer.status, 'Lost')
        
        # Change status back to Active
        customer.status = 'Active'
        db.session.commit()
        self.assertEqual(customer.status, 'Active')
    
    def test_lead_status_transitions(self):
        """Test lead status transitions"""
        # Create a lead
        lead = Lead(
            first_name='Lead',
            last_name='Status',
            email='leadstatus@example.com',
            status='New',
            assigned_to_id=self.admin_user.id,
            organization_id=self.default_org.id
        )
        db.session.add(lead)
        db.session.commit()
        
        # Change status to Contacted
        lead.status = 'Contacted'
        db.session.commit()
        self.assertEqual(lead.status, 'Contacted')
        
        # Change status to Qualified
        lead.status = 'Qualified'
        db.session.commit()
        self.assertEqual(lead.status, 'Qualified')
        
        # Change status to Converted
        lead.status = 'Converted'
        db.session.commit()
        self.assertEqual(lead.status, 'Converted')
    
    def test_customer_interactions(self):
        """Test customer interactions"""
        # Create a customer
        customer = Customer(
            first_name='Interaction',
            last_name='Test',
            email='interaction@example.com',
            status='Active',
            assigned_to_id=self.admin_user.id,
            organization_id=self.default_org.id
        )
        db.session.add(customer)
        db.session.commit()
        
        # Create multiple interactions
        interaction1 = Interaction(
            customer_id=customer.id,
            type='Email',
            description='First interaction',
            date=datetime.now() - timedelta(days=2),
            user_id=self.admin_user.id
        )
        db.session.add(interaction1)
        
        interaction2 = Interaction(
            customer_id=customer.id,
            type='Call',
            description='Second interaction',
            date=datetime.now() - timedelta(days=1),
            user_id=self.admin_user.id
        )
        db.session.add(interaction2)
        
        interaction3 = Interaction(
            customer_id=customer.id,
            type='Meeting',
            description='Third interaction',
            date=datetime.now(),
            user_id=self.admin_user.id
        )
        db.session.add(interaction3)
        
        db.session.commit()
        
        # Verify interactions
        interactions = Interaction.query.filter_by(customer_id=customer.id).order_by(Interaction.date.desc()).all()
        self.assertEqual(len(interactions), 3)
        self.assertEqual(interactions[0].type, 'Meeting')
        self.assertEqual(interactions[1].type, 'Call')
        self.assertEqual(interactions[2].type, 'Email')

if __name__ == '__main__':
    unittest.main() 