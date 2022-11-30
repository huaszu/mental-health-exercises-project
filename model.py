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
    pen_name = db.Column(db.String(120), nullable=True)
    # If we have a default pen_name, then don't exactly need nullable=True.
    # Better than having computation for if pen_name IS NULL, set default to
    # first_name?
    is_expert = db.Column(db.Boolean, nullable=False, default=False) # Not sure about default
    is_consumer = db.Column(db.Boolean, nullable=False, default=True)

    responses = db.relationship("ResponseToPrompt", back_populates="user") # A response belongs to one user
    creations = db.relationship("Exercise", back_populates="author") # An exercise has one author, who is a user
    push_subscriptions = db.relationship("PushSubscription", back_populates="user") # A push subscription belongs to one user
    # Currently not accommodating: A push subscription can have more than one user, if different users have logged in on the same browser
    notifications = db.relationship("Notification", back_populates="user") # A notification belongs to one user

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
    notifications = db.relationship("Notification", back_populates="exercise") # An exercise can have multiple notifications, for different users # Edge case example: If a user completes an exercise of freq 7 days today and then completes the same exercise tomorrow -> get notifications associated with both sittings

    def __repr__(self):
        return f'<Exercise exercise_id={self.exercise_id} title={self.title}>'


class Prompt(db.Model):
    """A prompt within an exercise."""

    __tablename__ = 'prompts'

    prompt_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    prompt_content = db.Column(db.Text, nullable=False)
    prompt_type = db.Column(db.String(120), nullable=False, default="long answer") # V0: Let's say all prompts for now get free-form text response
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
    time_completed_exercise = db.Column(db.DateTime(timezone=True), nullable=True) # Should not be nullable?
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.prompt_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False) # is nullable what allows not signed in user to use?  Forget that!  Only create responses in db that have user_id

    prompt = db.relationship("Prompt", back_populates="responses") # A prompt can have many responses, from different users or from the same user completing the same exercise multiple times
    user = db.relationship("User", back_populates="responses") # A user can have many responses

    def __repr__(self):
        return f'<ResponseToPrompt response_id={self.response_id} content={self.response_content}>'
        

class PushSubscription(db.Model):
    """A subscription to push notifications."""

    __tablename__ = 'push_subscriptions'

    id = db.Column(db.Integer,
                   autoincrement=True,
                   primary_key=True)
    subscription_json = db.Column(db.Text, nullable=False) # unique?
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    user = db.relationship("User", back_populates="push_subscriptions") # A user can have many push subscriptions, for instance if the same user signs in on many different browsers

    # users = db.relationship("User", back_populates="push_subscriptions") # A user can have many push subscriptions
    #   File "/Users/hsy/src/mental-health-exercises-project/env/lib/python3.10/site-packages/sqlalchemy/orm/decl_base.py", line 1142, in _declarative_constructor
    # raise TypeError(
    # TypeError: 'user' is an invalid keyword argument for PushSubscription

    # We expect subscription_json to be assigned a value that includes an
    # "endpoint", e.g., https://fcm.googleapis.com/fcm/send/ ... , an
    # "expirationTime", and "keys" - such as a "p256dh" key and an "auth" key.

    # subscription_json has the information that webpush takes in for the
    # subscription_info parameter.

    # https://developer.mozilla.org/en-US/docs/Web/API/PushSubscription/expirationTime

    def __repr__(self):
        return f'<PushSubscription id={self.id} subscription_json={self.subscription_json}>'


class Notification(db.Model):
    """A push notification."""

    __tablename__ = 'notifications'

    id = db.Column(db.Integer,
                   autoincrement=True,
                   primary_key=True)
    last_sent = db.Column(db.DateTime(timezone=True), nullable=False) # don't want default?
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.exercise_id'), nullable=False) # unique?  no because while each user should get only one notification for one exercise, multiple users can have notification enabled for that exercise
    # freq = db.Column(db.Integer, db.ForeignKey('exercises.frequency'), nullable=False) # sqlalchemy.exc.ProgrammingError: (psycopg2.errors.InvalidForeignKey) there is no unique constraint matching given keys for referenced table "exercises" (Background on this error at: http://sqlalche.me/e/14/f405)

    user = db.relationship("User", back_populates="notifications") # A user can have many notifications | but user can have many push subscriptions and the notification sends to user via (a) subscription(s) - current solution: send through all of that user's subscriptions
    exercise = db.relationship("Exercise", back_populates="notifications") # A notification belong to one exercise

    # freq = exercise.frequency # raise AttributeError(key) AttributeError: frequency

    def __repr__(self):
        return f'<Notification id={self.id} last_sent={self.last_sent}>'

# Notes on notif implementation:
# Have to be logged in to sign up for notifs - right now enforce in that we do
# not create a push subscription when there is no user_id -> look into the 
# ROLLBACKs in terminal?

# if logged in, don't worry about duplicates 
# user 1
# name of Exercise
# frequency 
# last notif sent
# if > 7 days, send a new notif
# update last notif column

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