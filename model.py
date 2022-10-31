"""Model for mental health exercises app."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    is_expert = db.Column(db.Boolean, nullable=False, default=False) # Not sure about default
    is_consumer = db.Column(db.Boolean, nullable=False, default=True)

    responses = db.relationship("ResponseToPrompt", back_populates="user") # Not sure 

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
    author = db.Column(db.String(120), db.ForeignKey('users.pen_name'), nullable=False)

    prompts = db.relationship("Prompt", back_populates="exercise")

    def __repr__(self):
        return f'<Exercise exercise_id={self.exercise_id} title={self.title}>'


class Prompt(db.Model): # Should be subclass of Exercise??
    """A prompt within an exercise."""

    __tablename__ = 'prompts'

    prompt_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    prompt_content = db.Column(db.Text, nullable=False)
    prompt_type = db.Column(db.String(120), nullable=False) 
    # prompt_type values could be "short answer", "long answer", 
    # "multiple choice - choose one", "multiple choice - choose multiple"
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.exercise_id'))

    exercise = db.relationship("Exercise", back_populates="prompts")
    responses = db.relationship("ResponseToPrompt", back_populates="prompt")

    def __repr__(self):
        return f'<Prompt prompt_id={self.prompt_id} content={self.prompt_content}>'


class ResponseToPrompt(db.Model): 
    """A response to a prompt."""

    __tablename__ = 'responses'

    response_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    response_content = db.Column(db.Text, nullable=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.prompt_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    prompt = db.relationship("Prompt", back_populates="responses")
    user = db.relationship("User", back_populates="responses")

    def __repr__(self):
        return f'<ResponseToPrompt response_id={self.response_id} content={self.response_content}>'
        

def connect_to_db(flask_app, db_uri="postgresql:///mental-health-platform", echo=True):
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