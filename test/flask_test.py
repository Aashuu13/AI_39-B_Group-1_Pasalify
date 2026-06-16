import unittest
from flask import Flask, Blueprint

class TestFlaskBasics(unittest.TestCase):
    def setUp(self):
        # Initialize the app instance
        self.app = Flask(__name__)
        self.app.secret_key = "secret_keyy"
        self.app.config['TESTING'] = True
        
        # Define the blueprint
        auth = Blueprint("auth", __name__)

        @auth.route("/login")
        def login():
            return "this is the login page"

        @auth.route("/home")
        def home():
            return "welcome home"

        # Register blueprint and create test client
        self.app.register_blueprint(auth)
        self.client = self.app.test_client()

    def test_login_route(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), "this is the login page")

    def test_home_route(self):
        response = self.client.get("/home")
        self.assertEqual(response.status_code, 200)
        self.assertIn("welcome home", response.data.decode("utf-8"))

if __name__ == "__main__":
    unittest.main()