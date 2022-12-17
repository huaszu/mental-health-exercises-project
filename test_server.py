"""Test suite."""

import server
import unittest
from flask import session
from model import connect_to_db, db


class HallOfMirrorsIntegrationTestCase(unittest.TestCase):
    """Integration tests: testing Flask server."""

    def setUp(self):
        print("(setUp ran)")
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True

    def tearDown(self):
        print("(tearDown ran)")
        return

    def test_homepage(self):
        result = self.client.get('/')
        self.assertIn(b'<h2 id="signin">Log In</h2>', result.data)

    # # Testing that the sample POST request to the route /add_exercise results in 'We love this exercise.' being rendered where the route redirects to, templates/all_exercises.html
    # def test_create_exercise_form(self):
    #     result = self.client.post('/add_exercise', data={'title': 'Best Exercise', 'description': 'We love this exercise.', 'prompt': 'How do you like my question?'})
    #     self.assertIn(b'We love this exercise.', result.data)
    #     # KeyError: 'user_id'


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
        # Without this line, "SQLALCHEMY_TRACK_MODIFICATIONS" showed up in 
        # error - relates to what is in model.py !

    def test_important_page(self):
        """Test important page."""

        result = self.client.get("/users/my_exercises", follow_redirects=True)
        # Should not make a difference whether follow_redirects=True or not
        self.assertIn(b"Here are all of the exercises you have completed and your past responses:", result.data)

    def test_create_exercise_page(self):
        """Test page for logged in user to author an exercise."""

        result = self.client.get("/create")
        self.assertIn(b"I want my exercise to have more prompts!", result.data)


if __name__ == '__main__':
    # If called like a script, run our tests
    unittest.main()