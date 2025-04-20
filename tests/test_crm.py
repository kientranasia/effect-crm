import unittest
import os
import tempfile
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Organization, Contact, Interaction, Role, Permission
from app.models.lead import Lead
from app.models.customer import Customer
from config import TestingConfig

class TestCRM(unittest.TestCase):
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
        admin_role = Role(name='Admin')
        db.session.add(admin_role)
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password='password',
            role_id=admin_role.id
        )
        db.session.add(admin_user)
        db.session.commit()
        
        self.admin_user = admin_user
        
        # Create default organization
        self.default_org = Organization(
            name='Test Organization',
            created_by_id=self.admin_user.id
        )
        db.session.add(self.default_org)
        db.session.commit()
        
        # Create default workspace
        default_workspace = Workspace(
            name='Default Workspace',
            description='Default workspace for testing',
            organization_id=self.default_org.id
        )
        db.session.add(default_workspace)
        db.session.commit()
        
        # Associate admin user with workspace
        db.session.execute(
            workspace_users.insert().values(
                user_id=self.admin_user.id,
                workspace_id=default_workspace.id
            )
        )
        db.session.commit()
        
        # Store references for later use
        self.admin_role = admin_role
        self.default_workspace = default_workspace
    
    def tearDown(self):
        # Close the database connection and remove the temporary file
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_contact_creation(self):
        """Test contact creation and properties"""
        # Create a new contact
        contact = Contact(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            phone='1234567890',
            job_title='Manager',
            organization_id=self.default_org.id,
            created_by_id=self.admin_user.id,
            stage='lead',
            source='website',
            requirements='Test requirements',
            interested_in='Test product'
        )
        
        db.session.add(contact)
        db.session.commit()
        
        # Test contact properties
        self.assertEqual(contact.full_name, 'Jane Smith')
        self.assertEqual(contact.email, 'jane@example.com')
        self.assertEqual(contact.stage, 'lead')
        self.assertEqual(contact.created_by, self.admin_user)
        self.assertEqual(contact.organization, self.default_org)
    
    def test_interaction_creation(self):
        """Test interaction creation and properties"""
        # Create a contact first
        contact = Contact(
            first_name='Robert',
            last_name='Johnson',
            email='robert@example.com',
            created_by_id=self.admin_user.id,
            stage='customer'
        )
        db.session.add(contact)
        db.session.commit()
        
        # Create an interaction
        interaction = Interaction(
            contact_id=contact.id,
            type='call',
            title='Initial Sales Call',
            description='Discussed product features and pricing',
            date=datetime.utcnow(),
            status='completed',
            outcome='Positive response',
            next_steps='Follow up with proposal',
            created_by_id=self.admin_user.id
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        # Test interaction properties
        self.assertEqual(interaction.type, 'call')
        self.assertEqual(interaction.title, 'Initial Sales Call')
        self.assertEqual(interaction.contact, contact)
        self.assertEqual(interaction.created_by, self.admin_user)
    
    def test_contact_stage_transition(self):
        """Test contact stage transitions"""
        # Create a contact
        contact = Contact(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            created_by_id=self.admin_user.id,
            stage='lead'
        )
        db.session.add(contact)
        db.session.commit()
        
        # Test stage transition to customer
        contact.update_stage('customer', self.admin_user.id)
        db.session.commit()
        
        self.assertEqual(contact.stage, 'customer')
        self.assertIsNotNone(contact.customer_since)
        self.assertEqual(contact.customer_status, 'active')
        
        # Test stage history
        import json
        history = json.loads(contact.stage_history)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['from_stage'], 'lead')
        self.assertEqual(history[0]['to_stage'], 'customer')
        self.assertEqual(history[0]['changed_by'], self.admin_user.id)

if __name__ == '__main__':
    unittest.main() 