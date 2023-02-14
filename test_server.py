"""Test suite for mental health exercises app."""

import server
import unittest
from flask import session
from model import connect_to_db


class HallOfMirrorsIntegrationTestCase(unittest.TestCase):
    """Integration tests: testing Flask server."""

    def setUp(self):
        """To do before every test."""

        print("(setUp ran)")
        self.client = server.app.test_client()
        # The `test_client` method technically comes from Werkzeug, a library
        # that Flask uses
        server.app.config['TESTING'] = True

    def tearDown(self):
        """To do after every test."""

        print("(tearDown ran)")
        return

    def test_homepage(self):
        """Test for expected HTML in homepage."""

        result = self.client.get('/')
        self.assertIn(b'<h2 id="signin">Log In</h2>', result.data)
        # `result.data` is the response string (html), returned in 
        # bytestring format (`b'`)


class FlaskTestsLoggedIn(unittest.TestCase):
    """Flask tests with user logged in to session."""

    def setUp(self):
        """To do before every test."""

        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = 'key'
        self.client = server.app.test_client()

        # Start each test with a user ID stored in the session.
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
        # Is 'user_id' the only key in session?  Yes

        connect_to_db(server.app)

    def test_important_page(self):
        """Test important page."""

        result = self.client.get("/users/my_exercises", follow_redirects=True)
        self.assertIn(b"Here are all of the exercises you have completed and your past responses:", result.data)

    def test_create_exercise_page(self):
        """Test page for logged in user to author an exercise."""

        result = self.client.get("/create")
        self.assertIn(b"I want my exercise to have more prompts!", result.data)


if __name__ == '__main__':
    # If called like a script, run tests
    unittest.main()