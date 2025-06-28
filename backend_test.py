
import unittest
import requests
from datetime import datetime, timedelta

class VacationGenieTests(unittest.TestCase):
    """Test suite for the Vacation Genie Flask application"""
    
    BASE_URL = "http://127.0.0.1:5000"
    
    def test_home_page_loads(self):
        """Test that the home page loads successfully"""
        response = requests.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Vacation Genie", response.text)
        self.assertIn("Plan Your Perfect Trip", response.text)
    
    def test_login_page_loads(self):
        """Test that the login page loads successfully"""
        response = requests.get(f"{self.BASE_URL}/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Log in", response.text)
        self.assertIn("Email", response.text)
        self.assertIn("Password", response.text)
    
    def test_signup_page_loads(self):
        """Test that the sign-up page loads successfully"""
        response = requests.get(f"{self.BASE_URL}/sign-up")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Create Account", response.text)
        self.assertIn("First Name", response.text)
        self.assertIn("Last Name", response.text)
    
    def test_login_functionality(self):
        """Test login functionality with correct credentials"""
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        
        session = requests.Session()
        response = session.post(f"{self.BASE_URL}/login", data=login_data)
        
        # Note: This test might fail due to the secret key issue
        # The application should redirect to home page after successful login
        self.assertEqual(response.status_code, 200)
        self.assertIn("Vacation Genie", response.text)
    
    def test_search_form_submission(self):
        """Test the travel search form submission"""
        # Get tomorrow's date for departure and day after for return
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        
        form_data = {
            "origin": "New York, NY",
            "destination": "Paris, France",
            "departureDate": tomorrow,
            "returnDate": day_after
        }
        
        session = requests.Session()
        response = session.post(f"{self.BASE_URL}/", data=form_data)
        
        # Note: This test might fail due to the secret key issue
        # The application should return the home page with itinerary results
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains the itinerary
        self.assertIn("Your Perfect Itinerary", response.text)
        self.assertIn("Paris, France", response.text)
        self.assertIn("New York, NY", response.text)

if __name__ == "__main__":
    unittest.main()