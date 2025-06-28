import unittest
import requests
from datetime import datetime, timedelta
import random
import string

class VacationGenieTests(unittest.TestCase):
    """Test suite for the Vacation Genie Flask application"""
    
    BASE_URL = "http://localhost:8001"
    
    def setUp(self):
        """Set up for each test"""
        self.session = requests.Session()
        # Generate a random email for signup tests
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.test_email = f"test_{random_suffix}@example.com"
        self.test_password = "TestPassword123!"
        self.test_first_name = "Test"
        self.test_last_name = "User"
    
    def test_1_home_redirects_when_not_authenticated(self):
        """Test that the home page redirects to login when not authenticated"""
        response = self.session.get(f"{self.BASE_URL}/", allow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers.get('Location', ''))
    
    def test_2_login_page_loads(self):
        """Test that the login page loads successfully"""
        response = self.session.get(f"{self.BASE_URL}/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Log in", response.text)
        self.assertIn("Email", response.text)
        self.assertIn("Password", response.text)
    
    def test_3_signup_page_loads(self):
        """Test that the sign-up page loads successfully"""
        response = self.session.get(f"{self.BASE_URL}/sign-up")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Create Account", response.text)
        self.assertIn("First Name", response.text)
        self.assertIn("Last Name", response.text)
    
    def test_4_signup_functionality(self):
        """Test signup functionality with valid data"""
        signup_data = {
            "email": self.test_email,
            "firstName": self.test_first_name,
            "lastName": self.test_last_name,
            "password1": self.test_password,
            "password2": self.test_password
        }
        
        response = self.session.post(f"{self.BASE_URL}/sign-up", data=signup_data, allow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Account created", response.text.lower())
    
    def test_5_login_with_invalid_credentials(self):
        """Test login functionality with incorrect credentials"""
        login_data = {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
        
        response = self.session.post(f"{self.BASE_URL}/login", data=login_data, allow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("invalid email or password", response.text.lower())
    
    def test_6_login_with_valid_credentials(self):
        """Test login functionality with correct credentials"""
        # First try with default admin credentials
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        
        response = self.session.post(f"{self.BASE_URL}/login", data=login_data, allow_redirects=True)
        
        # If admin login fails, try with our test user
        if "invalid email or password" in response.text.lower():
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            response = self.session.post(f"{self.BASE_URL}/login", data=login_data, allow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("vacation genie", response.text.lower())
        self.assertIn("your ai-powered travel companion", response.text.lower())
    
    def test_7_home_page_after_login(self):
        """Test that the home page loads after login"""
        # Login first
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        self.session.post(f"{self.BASE_URL}/login", data=login_data)
        
        # Then access home page
        response = self.session.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Vacation Genie", response.text)
        self.assertIn("I'm planning a trip from", response.text)
    
    def test_8_trip_planning_form_validation(self):
        """Test form validation for the trip planning form"""
        # Login first
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        self.session.post(f"{self.BASE_URL}/login", data=login_data)
        
        # Test with missing origin
        form_data = {
            "origin": "",
            "destination": "Paris, France",
            "departureDate": datetime.now().strftime('%Y-%m-%d'),
            "returnDate": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        }
        
        response = self.session.post(f"{self.BASE_URL}/", data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("please enter an origin city", response.text.lower())
        
        # Test with past departure date
        past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        form_data = {
            "origin": "New York, NY",
            "destination": "Paris, France",
            "departureDate": past_date,
            "returnDate": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        }
        
        response = self.session.post(f"{self.BASE_URL}/", data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("departure date cannot be in the past", response.text.lower())
        
        # Test with return date before departure date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        form_data = {
            "origin": "New York, NY",
            "destination": "Paris, France",
            "departureDate": tomorrow,
            "returnDate": datetime.now().strftime('%Y-%m-%d')
        }
        
        response = self.session.post(f"{self.BASE_URL}/", data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("return date must be after departure date", response.text.lower())
    
    def test_9_successful_trip_planning(self):
        """Test successful trip planning form submission"""
        # Login first
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        self.session.post(f"{self.BASE_URL}/login", data=login_data)
        
        # Get tomorrow's date for departure and a week later for return
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
        
        form_data = {
            "origin": "New York, NY",
            "destination": "Paris, France",
            "departureDate": tomorrow,
            "returnDate": next_week
        }
        
        response = self.session.post(f"{self.BASE_URL}/", data=form_data)
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains the itinerary
        self.assertIn("your perfect itinerary", response.text.lower())
        self.assertIn("paris, france", response.text.lower())
        self.assertIn("new york, ny", response.text.lower())
        self.assertIn("day 1", response.text.lower())
    
    def test_10_logout_functionality(self):
        """Test logout functionality"""
        # Login first
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        self.session.post(f"{self.BASE_URL}/login", data=login_data)
        
        # Then logout
        response = self.session.get(f"{self.BASE_URL}/logout", allow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("you have been logged out", response.text.lower())
        
        # Verify we're redirected to login when accessing home
        response = self.session.get(f"{self.BASE_URL}/", allow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers.get('Location', ''))

if __name__ == "__main__":
    unittest.main()