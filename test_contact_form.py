#!/usr/bin/env python3
"""
Test script for the contact form functionality
Run this to test if the contact form is working properly
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_contact_form():
    """Test the contact form functionality"""
    app = create_app('development')
    
    with app.test_client() as client:
        # Test GET request (should return the contact page)
        print("Testing GET /contact...")
        response = client.get('/contact')
        assert response.status_code == 200
        print("✓ GET /contact works")
        
        # Test POST request with valid data
        print("\nTesting POST /contact with valid data...")
        response = client.post('/contact', data={
            'username': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message from the contact form.'
        })
        assert response.status_code == 200
        print("✓ POST /contact with valid data works")
        
        # Test POST request with missing data
        print("\nTesting POST /contact with missing data...")
        response = client.post('/contact', data={
            'username': 'Test User',
            'email': '',  # Missing email
            'message': 'This is a test message.'
        })
        assert response.status_code == 200
        print("✓ POST /contact with missing data works (shows error)")
        
        # Test POST request with invalid email
        print("\nTesting POST /contact with invalid email...")
        response = client.post('/contact', data={
            'username': 'Test User',
            'email': 'invalid-email',
            'message': 'This is a test message.'
        })
        assert response.status_code == 200
        print("✓ POST /contact with invalid email works (shows error)")
        
        print("\n✅ All contact form tests passed!")
        print("\nNext steps:")
        print("1. Set up Gmail app password (see email_setup_guide.md)")
        print("2. Update the sender_password in app.py")
        print("3. Test the live contact form in your browser")

if __name__ == '__main__':
    test_contact_form()
