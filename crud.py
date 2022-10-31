'''CRUD operations.'''

from model import db, User, connect_to_db
from datetime import datetime


def create_user(email, password, first_name, last_name, is_expert, is_consumer, pen_name):
    """Create and return a new user."""

    user = User(email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name,
                pen_name=pen_name,
                is_expert=is_expert,
                is_consumer=is_consumer)

    return user


def get_users():
    """Return all users from database."""

    return User.query.all()    


def get_user_by_id(user_id):
    """Return user with user_id."""

    return User.query.get(user_id)


if __name__ == '__main__':
    from server import app
    connect_to_db(app)