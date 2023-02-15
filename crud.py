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

    # `current` is when the scheduled send_push() function begins to run.
    # Compare `current` to (the time the notification was last sent, plus the 
    # days that a user is recommended to go before revisiting the exercise).
    # If `current` is later in time in that comparison, then this 
    # notification is due to be sent again, to encourage the user to revisit
    # the exercise

    notifs_to_send = []
    notifications = Notification.query.all()
    for notification in notifications:
        next_date = notification.last_sent + timedelta(days=notification.exercise.frequency)
        if next_date < current:
            notifs_to_send.append(notification)
    # print(notifs_to_send)

    return notifs_to_send


def get_notifications_to_send_for_test(current):
    """Return notifications to deliver for testing purposes."""

    # Problem solving in collaboration with Jared B: 
    # get list of all notifications
    # for each notification:
    #   Check if that particular notification needs to be sent
    #   get the date that this particular notification was LAST sent on
    #   calculate the nextDate (when it should go out)
    #   if nextDate < current:
    #       include that notification in the list
    #   compare that date to the current time
    #   Add to a list if so
    # Return all notifications in the list

    notifs_to_send = []
    notifications = Notification.query.all()
    for notification in notifications:
        next_date = notification.last_sent + timedelta(seconds=notification.exercise.frequency)
        if next_date < current:
            notifs_to_send.append(notification)
    print(notifs_to_send)
    return notifs_to_send

    #print(Notification.query.filter((current - Notification.last_sent) > timedelta(seconds=Exercise.frequency)).all())
                                                                                            # Works because SQLAlchemy knows which exercise based on notification having relationship to exercise
    #return Notification.query.filter((current - Notification.last_sent) > timedelta(seconds=Exercise.frequency)).all()


def get_subscriptions_from_notification(notification):
    """Return push subscriptions of user to whom notification belongs."""

    subscriptions = PushSubscription.query.filter(notification.user_id == PushSubscription.user_id).all()

    return subscriptions
    

def get_users_notify():
    """Return users to be notified."""

    pass


# # Deprecated
# def get_users_for_push():
#     """Return users who should get push notifications."""

#     pacific_time = pytz.timezone("America/Los_Angeles")
#     now = datetime.now(pacific_time)
#     print(now)

#     # A dictionary where keys are users and each value is a set of exercises 
#     # about which that user should be notified.  Put exercises in set because 
#     # in one scheduled push, we want each user to get one notification per 
#     # exercise.
#     users_exercises_push = {}

#     # There could be efficiency improvements in going through all notifs
#     for notification in Notification.query.all():
#         print(notification.user)
#         print(notification.exercise)

#         # gap is a timedelta object
#         gap = now - notification.last_sent
#         print(gap)
#         print(notification.exercise.frequency)
#         print(timedelta(days=notification.exercise.frequency))

#         if gap > timedelta(days=notification.exercise.frequency):
#             users_exercises_push[notification.user] = users_exercises_push.get(notification.user, {"exercises": set()})["exercises"].add(notification.exercise)
#             # Can an object, can an instance of a class be a dictionary key?  Immutable?
#               # Make another key in inner dictionary - "subscription" and value is PushSubscription object(s)
#               #     Was going to in function update_subscription_data_on_users_for_push()

#         # Data structures are fun.  Am I making Python do too much?  
#         # Use Object-Relational Mapping! 

#     print(users_exercises_push)

#     return users_exercises_push


# # Deprecated
# def update_subscription_data_on_users_for_push():
#     """Return users who get notifications, with respective subscription data."""

#     pass


if __name__ == '__main__':
    from server import app
    connect_to_db(app)

    # exercises_of_user = []
    # for response in ResponseToPrompt.query.first().user.responses:
    #     response.prompt.exercise =
    #     for prompt in response.prompt:
    #         print(prompt)
    #         exercise = prompt.exercise
    #         print(exercise)
    #         if exercise not in exercises_of_user:
    #             exercises_of_user.append(exercise)
    # print(exercises_of_user)
    # # print_exercise_responses(User.query.first(), choice(exercises_of_user))

    # # print(ResponseToPrompt.query.first().user.responses)

    # print_user_prompts(User.query.filter(User.user_id == 5))