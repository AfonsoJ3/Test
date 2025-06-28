
import unittest
import requests
from datetime import datetime, timedelta

class VacationGenieTests(unittest.TestCase):
    """Test suite for the Vacation Genie Flask application"""
    
    BASE_URL = "http://127.0.0.1:5000"
    
    def test_01_home_page_redirects_to_login_when_not_authenticated(self):
        """Test that the home page redirects to login when not authenticated"""
        session = requests.Session()
        response = session.get(f"{self.BASE_URL}/", allow_redirects=True)
        self.assertEqual(response.url, f"{self.BASE_URL}/login")
        self.assertIn("Log in", response.text)
    
    def test_02_login_page_loads(self):
        """Test that the login page loads successfully"""
        response = requests.get(f"{self.BASE_URL}/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Log in", response.text)
        self.assertIn("Email", response.text)
        self.assertIn("Password", response.text)
    
    def test_03_signup_page_loads(self):
        """Test that the sign-up page loads successfully"""
        response = requests.get(f"{self.BASE_URL}/sign-up")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Create Account", response.text)
        self.assertIn("First Name", response.text)
        self.assertIn("Last Name", response.text)
    
    def test_04_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
        
        session = requests.Session()
        response = session.post(f"{self.BASE_URL}/login", data=login_data, allow_redirects=True)
        
        # Should stay on login page with error message
        self.assertIn("Invalid email or password", response.text)
    
    def test_05_login_with_valid_credentials(self):
        """Test login functionality with correct credentials"""
        login_data = {
            "email": "admin@example.com",
            "password": "password"
        }
        
        session = requests.Session()
        response = session.post(f"{self.BASE_URL}/login", data=login_data, allow_redirects=True)
        
        # Should redirect to home page after successful login
        self.assertEqual(response.url, f"{self.BASE_URL}/")
        self.assertIn("Vacation Genie", response.text)
        self.assertIn("Plan Your Perfect Trip", response.text)
        
        # Check that logout link is present in the navbar
        self.assertIn('id="logout"', response.text)
        self.assertNotIn('id="login"', response.text)
        
        return session  # Return the authenticated session for further tests
    
    def test_06_logout_functionality(self):
        """Test logout functionality"""
        # First login to get an authenticated session
        session = self.test_05_login_with_valid_credentials()
        
        # Now logout
        response = session.get(f"{self.BASE_URL}/logout", allow_redirects=True)
        
        # Should redirect to login page
        self.assertEqual(response.url, f"{self.BASE_URL}/login")
        self.assertIn("Log in", response.text)
        self.assertIn("You have been logged out successfully", response.text)
        
        # Try to access home page again, should redirect to login
        response = session.get(f"{self.BASE_URL}/", allow_redirects=True)
        self.assertEqual(response.url, f"{self.BASE_URL}/login")
    
    def test_07_signup_form_validation(self):
        """Test sign up form validation"""
        # Test with short email
        signup_data = {
            "email": "a@b",
            "firstName": "Test",
            "lastName": "User",
            "password1": "password123456",
            "password2": "password123456"
        }
        
        session = requests.Session()
        response = session.post(f"{self.BASE_URL}/sign-up", data=signup_data, allow_redirects=True)
        self.assertIn("Email mush be greater than 4 characters", response.text)
        
        # Test with short first name
        signup_data["email"] = "test@example.com"
        signup_data["firstName"] = "T"
        response = session.post(f"{self.BASE_URL}/sign-up", data=signup_data, allow_redirects=True)
        self.assertIn("First name mush be greater than 1 character", response.text)
        
        # Test with short last name
        signup_data["firstName"] = "Test"
        signup_data["lastName"] = "U"
        response = session.post(f"{self.BASE_URL}/sign-up", data=signup_data, allow_redirects=True)
        self.assertIn("Last name mush be greater than 2 character", response.text)
        
        # Test with mismatched passwords
        signup_data["lastName"] = "User"
        signup_data["password2"] = "differentpassword"
        response = session.post(f"{self.BASE_URL}/sign-up", data=signup_data, allow_redirects=True)
        self.assertIn("Passwords don't match", response.text)
        
        # Test with short password
        signup_data["password1"] = "short"
        signup_data["password2"] = "short"
        response = session.post(f"{self.BASE_URL}/sign-up", data=signup_data, allow_redirects=True)
        self.assertIn("Password must be at least 12 characters", response.text)
        
        # Test with valid data
        signup_data["password1"] = "validpassword12345"
        signup_data["password2"] = "validpassword12345"
        response = session.post(f"{self.BASE_URL}/sign-up", data=signup_data, allow_redirects=True)
        
        # Should redirect to login page with success message
        self.assertEqual(response.url, f"{self.BASE_URL}/login")
        self.assertIn("Account created! Please log in", response.text)
    
    def test_08_search_form_validation(self):
        """Test the travel search form validation"""
        # First login to get an authenticated session
        session = self.test_05_login_with_valid_credentials()
        
        # Test with missing origin
        form_data = {
            "origin": "",
            "destination": "Paris, France",
            "departureDate": "2025-04-01",
            "returnDate": "2025-04-07"
        }
        
        response = session.post(f"{self.BASE_URL}/", data=form_data, allow_redirects=True)
        self.assertIn("Please enter an origin city", response.text)
        
        # Test with missing destination
        form_data["origin"] = "New York, NY"
        form_data["destination"] = ""
        response = session.post(f"{self.BASE_URL}/", data=form_data, allow_redirects=True)
        self.assertIn("Please enter a destination city", response.text)
        
        # Test with missing departure date
        form_data["destination"] = "Paris, France"
        form_data["departureDate"] = ""
        response = session.post(f"{self.BASE_URL}/", data=form_data, allow_redirects=True)
        self.assertIn("Please select a departure date", response.text)
        
        # Test with missing return date
        form_data["departureDate"] = "2025-04-01"
        form_data["returnDate"] = ""
        response = session.post(f"{self.BASE_URL}/", data=form_data, allow_redirects=True)
        self.assertIn("Please select a return date", response.text)
        
        # Test with past departure date
        past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        form_data["departureDate"] = past_date
        form_data["returnDate"] = "2025-04-07"
        response = session.post(f"{self.BASE_URL}/", data=form_data, allow_redirects=True)
        self.assertIn("Departure date cannot be in the past", response.text)
        
        # Test with return date before departure date
        form_data["departureDate"] = "2025-04-07"
        form_data["returnDate"] = "2025-04-01"
        response = session.post(f"{self.BASE_URL}/", data=form_data, allow_redirects=True)
        self.assertIn("Return date must be after departure date", response.text)
    
    def test_09_search_form_submission(self):
        """Test the travel search form submission with valid data"""
        # First login to get an authenticated session
        session = self.test_05_login_with_valid_credentials()
        
        # Valid form data
        form_data = {
            "origin": "New York, NY",
            "destination": "Paris, France",
            "departureDate": "2025-04-01",
            "returnDate": "2025-04-07"
        }
        
        response = session.post(f"{self.BASE_URL}/", data=form_data, allow_redirects=True)
        
        # Check if the response contains the itinerary
        self.assertIn("Your Perfect Itinerary", response.text)
        self.assertIn("Paris, France", response.text)
        self.assertIn("New York, NY", response.text)
        self.assertIn("Perfect! Your itinerary", response.text)

if __name__ == "__main__":
    unittest.main()