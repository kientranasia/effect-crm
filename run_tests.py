import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import the tests
from tests.test_crm import CRMTests

if __name__ == '__main__':
    # Run the tests
    unittest.main() 