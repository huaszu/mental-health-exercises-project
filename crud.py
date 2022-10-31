'''CRUD operations.'''

from model import db, User, Exercise, Prompt, connect_to_db
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


def create_exercise(title, description, frequency, time_limit_per_sitting, author_id):
    """Create and return a new exercise."""

    exercise = Exercise(title=title, 
                        description=description, 
                        frequency=frequency, 
                        time_limit_per_sitting=time_limit_per_sitting,
                        author_id=author_id)

    return exercise


def get_exercises():
    """Return all exercises from database."""

    return Exercise.query.all()    


def get_exercise_by_id(exercise_id):
    """Return exercise with exercise_id."""

    return Exercise.query.get(exercise_id)


def create_prompt(prompt_content, prompt_type, exercise, author):
    """Create and return a new prompt."""

    prompt = Prompt(prompt_content=prompt_content, 
                        prompt_type=prompt_type, 
                        exercise=exercise, 
                        author=author)

    return prompt


def get_prompts():
    """Return all prompts from database."""

    return Prompt.query.all()    


def get_prompt_by_id(prompt_id):
    """Return prompt with prompt_id."""

    return Prompt.query.get(prompt_id)


if __name__ == '__main__':
    from server import app
    connect_to_db(app)