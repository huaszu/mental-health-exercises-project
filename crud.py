"""CRUD operations for mental health exercises app."""

from model import db, User, Exercise, Prompt, ResponseToPrompt, PushSubscription, Notification, connect_to_db
from datetime import timedelta


def create_user(email, password, first_name, last_name, is_expert=False, is_consumer=True, pen_name=None):
    """Create and return a new user."""

    user = User(email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_expert=is_expert,
                is_consumer=is_consumer,
                pen_name=pen_name)

    return user


def get_users():
    """Return all users from database."""

    return User.query.all()    


def get_user_by_id(user_id):
    """Return user by `user_id.`"""

    return User.query.get(user_id)


def get_user_by_email(email):
    """Return user by `email`."""

    return User.query.filter(User.email == email).first()


def create_exercise(title, description, author, frequency=None, time_limit_per_sitting=None):
    """Create and return a new exercise."""

    exercise = Exercise(title=title, 
                        description=description,
                        author=author, 
                        frequency=frequency, 
                        time_limit_per_sitting=time_limit_per_sitting)

    return exercise


def get_exercises():
    """Return all exercises from database."""

    return Exercise.query.all()    


def get_exercise_by_id(exercise_id):
    """Return exercise by `exercise_id`."""

    return Exercise.query.get(exercise_id)


def create_prompt(prompt_content, exercise, prompt_type="long answer"):
    """Create and return a new prompt."""

    prompt = Prompt(prompt_content=prompt_content, 
                    prompt_type=prompt_type, 
                    exercise=exercise)

    return prompt


def get_prompts():
    """Return all prompts from database."""

    return Prompt.query.all()    


def get_prompt_by_id(prompt_id):
    """Return prompt by `prompt_id`."""

    return Prompt.query.get(prompt_id)


def get_prompts_by_exercise(exercise_id):
    """Return prompts by `exercise_id`."""

    return Prompt.query.filter(Prompt.exercise_id == exercise_id).all()


def create_response(response_content, prompt, user, time_completed_exercise):
    """Create and return a new response."""

    response = ResponseToPrompt(response_content=response_content, 
                                prompt=prompt, 
                                user=user, 
                                time_completed_exercise=time_completed_exercise)

    return response


def get_responses():
    """Return all responses from database."""

    return ResponseToPrompt.query.all()    


def get_response_by_id(response_id):
    """Return response by `response_id`."""

    return ResponseToPrompt.query.get(response_id)


def get_responses_by_user_id(user_id):
    """Return responses by `user_id`."""

    return ResponseToPrompt.query.filter(ResponseToPrompt.user_id == user_id).all()


def print_exercise_responses_of_user(user_id, exercise_id):
    """Print all of user's responses to prompts for this exercise."""

    prompt_response_pairs = []

    # List of responses
    responses = ResponseToPrompt.query.filter(ResponseToPrompt.user_id == user_id).join(Prompt).filter(Prompt.exercise_id == exercise_id).all()

    for response in responses:
        tup = (response.prompt.prompt_content, response.response_content)
        prompt_response_pairs.append(tup)

    for tup in prompt_response_pairs:
        # Unpack the tuple to make the print more useful for engineers
        (prompt_content, response_content) = tup
        print(f'Prompt: {prompt_content} Response: {response_content}')
    
    return prompt_response_pairs


def print_exercises_of_user(user_id):
    """Print all exercises user has responded to."""

    exercises = []

    # List of responses of user
    responses = ResponseToPrompt.query.filter(ResponseToPrompt.user_id == user_id).join(Prompt).all()

    for response in responses:
        print("Exercise Title:", response.prompt.exercise.title)
        exercises.append(response.prompt.exercise)
    
    return exercises


def get_unique_exercises_of_user(user_id):
    """Return unique exercises user has responded to."""

    exercises = set() # Note: exercises will be unordered

    responses = ResponseToPrompt.query.filter(ResponseToPrompt.user_id == user_id).join(Prompt).all()

    for response in responses:
        exercises.add(response.prompt.exercise)
    
    return exercises


def create_push_subscription(subscription_json, user):
    """Create and return a new subscription to push notifications."""

    subscription = PushSubscription(subscription_json=subscription_json,
                                    user=user)

    return subscription


def get_subscriptions():
    """Return all subscriptions from database."""

    return PushSubscription.query.all()  


def get_first_subscription(subscription_json):
    """Return first subscription to push notifications."""

    first_subscription = PushSubscription.query.filter(PushSubscription.subscription_json == subscription_json).first()

    return first_subscription


def get_subscription_by_id(subscription_id):
    """Return subscription by `subscription_id`."""

    return PushSubscription.query.get(subscription_id)


def create_notification(user, exercise, last_sent):
    """Create and return a new notification."""

    notification = Notification(user=user,
                                exercise=exercise,
                                last_sent=last_sent)

    return notification


def get_notifications():
    """Return all notifications from database."""

    return Notification.query.all() 


def get_notification_by_id(notification_id):
    """Return notification by `notification_id`."""

    return Notification.query.get(notification_id)


def get_notifications_to_send(current):
    """Return notifications to send."""

    # `current` is when the scheduled `server.send_push()` function begins to run

    notifs_to_send = []
    notifications = Notification.query.all()
    for notification in notifications:
        # Calculate when notification should next be sent to prepare for 
        # comparison with `current`
        next_date = notification.last_sent + timedelta(days=notification.exercise.frequency)
        # If `current` is later in time than when the notification should
        # next be sent, then this notification is due to be sent again, to 
        # encourage the user to revisit the exercise
        if next_date < current:
            notifs_to_send.append(notification)
    # print(notifs_to_send)

    # TODO: Optimize the database call.  Why?
    # Because filtering in the database would take advantage of the db's index.
    # And returning lots of data from the db to code takes more memory and time.

    # Idea: Filter for notifications where the time gap that has transpired 
    # from the time the notification was last sent to `current` is greater 
    # than the gap recommended based on how often the exercise should be 
    # completed. 
    # Therefore, instead of `Notification.query.all()`:
    
    # Alternative 1: 
    # `Notification.query.filter((current - Notification.last_sent) > timedelta(hours=Notification.Exercise.frequency)).all())`
    # Testing this approach gave errors.

    # Alternative 2: Based on SQLAlchemy documentation, I had a hypothesis that
    # SQLAlchemy can identify the exercise based on a notification having a 
    # relationship to an exercise.  I tried simplifying Alternative 1 to
    # `Notification.query.filter((current - Notification.last_sent) > timedelta(hours=Exercise.frequency)).all())`
    # Testing this approach gave errors.

    # Next step: Further investigation of how SQLAlchemy works to come up with
    # better alternatives.

    return notifs_to_send

get_notifications_to_send(current)

def get_subscriptions_from_notification(notification):
    """Return push subscriptions of user to whom notification belongs."""

    subscriptions = PushSubscription.query.filter(notification.user_id == PushSubscription.user_id).all()

    return subscriptions


if __name__ == '__main__':
    from server import app
    connect_to_db(app)