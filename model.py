"""Model for mental health exercises app."""

from flask_sqlalchemy import SQLAlchemy

# Initialize object
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
    is_expert = db.Column(db.Boolean, nullable=False, default=False)
    is_consumer = db.Column(db.Boolean, nullable=False, default=True)

    responses = db.relationship("ResponseToPrompt", back_populates="user") # A response belongs to one user
    creations = db.relationship("Exercise", back_populates="author") # An exercise has one author, who is a user
    push_subscriptions = db.relationship("PushSubscription", back_populates="user") # A push subscription belongs to one user
    # Currently not accommodating: A push subscription can have more than one user, if different users have logged in on the same browser
    notifications = db.relationship("Notification", back_populates="user") # A notification belongs to one user

    # Return string containing printable representation of object
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
    frequency = db.Column(db.Integer, nullable=True)
    time_limit_per_sitting = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    prompts = db.relationship("Prompt", back_populates="exercise") # A prompt belongs to one exercise
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
    # V0 default: Let's say all prompts for now get free-form text response
    prompt_type = db.Column(db.String(120), nullable=False, default="long answer")
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    prompt = db.relationship("Prompt", back_populates="responses") # A prompt can have many responses, from different users and/or from the same user completing the same exercise multiple times
    user = db.relationship("User", back_populates="responses") # A user can have many responses

    def __repr__(self):
        return f'<ResponseToPrompt response_id={self.response_id} content={self.response_content}>'
        

class PushSubscription(db.Model):
    """A subscription to push notifications."""

    __tablename__ = 'push_subscriptions'

    id = db.Column(db.Integer,
                   autoincrement=True,
                   primary_key=True)

    # `subscription_json` is assigned a value that includes an "endpoint", an
    # "expirationTime", and "keys" - such as a "p256dh" key and an "auth" key.
    # An example of an "endpoint" may begin with 
    # "https://fcm.googleapis.com/fcm/send/".
    # `subscription_json` has the information that webpush() from pywebpush
    # library takes in for the `subscription_info` parameter.
    # https://developer.mozilla.org/en-US/docs/Web/API/PushSubscription
    subscription_json = db.Column(db.Text, nullable=False)
    # `user_id` is not nullable to enforce that a user has to be logged in to 
    # sign up for notifications
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    user = db.relationship("User", back_populates="push_subscriptions") # A user can have many push subscriptions, for instance if the same user signs in on many different browsers

    def __repr__(self):
        return f'<PushSubscription id={self.id} subscription_json={self.subscription_json}>'


class Notification(db.Model):
    """A push notification."""

    __tablename__ = 'notifications'

    id = db.Column(db.Integer,
                   autoincrement=True,
                   primary_key=True)
    last_sent = db.Column(db.DateTime(timezone=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.exercise_id'), nullable=False)

    user = db.relationship("User", back_populates="notifications") # A user can have many notifications
    exercise = db.relationship("Exercise", back_populates="notifications") # A notification belongs to one exercise

    def __repr__(self):
        return f'<Notification id={self.id} last_sent={self.last_sent}>'


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