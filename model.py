"""Model for mental health exercises app."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    pen_name = db.Column(db.String(120), nullable=False)
    # If we have a default pen_name, then don't exactly need nullable=True.
    # Better than having computation for if pen_name IS NULL, set default to
    # first_name?
    is_expert = db.Column(db.Boolean, nullable=False, default=True) # Not sure about default
    is_consumer = db.Column(db.Boolean, nullable=False, default=True)

    responses = db.relationship("ResponseToPrompt", back_populates="user") # A response belongs to one user
    creations = db.relationship("Exercise", back_populates="author") # An exercise has one author, who is a user

    def __repr__(self):
        return f'<User user_id={self.user_id} email={self.email} is_expert={self.is_expert}>'


class Exercise(db.Model):
    """An exercise."""

    __tablename__ = 'exercises'

    exercise_id = db.Column(db.Integer,
                            autoincrement=True,
                            primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    frequency = db.Column(db.Integer, nullable=True) # Theoretically could set a default
    time_limit_per_sitting = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    # Having author_id as a column does not mean we need author_id to be a parameter in create_exercise() fn

    prompts = db.relationship("Prompt", back_populates="exercise") # A prompt belongs to one exercise
    # Does prompts need to be a parameter in create_exercise() fn?  Theory: No, because when we create a prompt, we associate prompt to an exercise 
    author = db.relationship("User", back_populates="creations") # A user can author many exercises

    def __repr__(self):
        return f'<Exercise exercise_id={self.exercise_id} title={self.title}>'


class Prompt(db.Model):
    """A prompt within an exercise."""

    __tablename__ = 'prompts'

    prompt_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    prompt_content = db.Column(db.Text, nullable=False)
    prompt_type = db.Column(db.String(120), nullable=True, default="long answer") # V0: Let's say all prompts for now get free-form text response
    # prompt_type values could be "short answer", "long answer", 
    # "multiple choice - choose one", "multiple choice - choose multiple"
    # Potentially in future: one prompt to many prompt options.  Another table
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.exercise_id'), nullable=False)

    exercise = db.relationship("Exercise", back_populates="prompts") # An exercise can have many prompts
    responses = db.relationship("ResponseToPrompt", back_populates="prompt") # A response belongs to one prompt

    def __repr__(self):
        return f'<Prompt prompt_id={self.prompt_id} content={self.prompt_content}>'


class ResponseToPrompt(db.Model): 
    """A response to a prompt."""

    __tablename__ = 'responses'

    response_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    response_content = db.Column(db.Text, nullable=True)
    time_completed_exercise = db.Column(db.DateTime(timezone=True), nullable=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.prompt_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False) # is nullable what allows not signed in user to use?  Forget that!  Only create responses in db that have user_id

    prompt = db.relationship("Prompt", back_populates="responses") # A prompt can have many responses, from different users or from the same user completing the same exercise multiple times
    user = db.relationship("User", back_populates="responses") # A user can have many responses

    def __repr__(self):
        return f'<ResponseToPrompt response_id={self.response_id} content={self.response_content}>'
        

class PushSubscription(db.Model):
    """Subscription to push notification"""

    __tablename__ = 'push_subscription'

    id = db.Column(db.Integer,
                   autoincrement=True,
                   primary_key=True)
    subscription_json = db.Column(db.Text, nullable=False)
    # We expect subscription_json to be assigned a value that includes an
    # "endpoint", e.g., https://fcm.googleapis.com/fcm/send/ ... , an
    # "expirationTime", and "keys" - such as a "p256dh" key and an "auth" key.
    
    # https://developer.mozilla.org/en-US/docs/Web/API/PushSubscription/expirationTime

    def __repr__(self):
        return f'<PushSubscription id={self.id} subscription_json={self.subscription_json}>'


def connect_to_db(flask_app, db_uri="postgresql:///health", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)