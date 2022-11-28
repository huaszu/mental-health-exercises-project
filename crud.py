'''CRUD operations.'''

from model import db, User, Exercise, Prompt, ResponseToPrompt, PushSubscription, Notification, connect_to_db
from datetime import datetime, date, timedelta
import pytz
from random import choice


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
    """Return user with user_id."""

    return User.query.get(user_id)


def get_user_by_email(email):
    """Return a user by email."""

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
    """Return exercise with exercise_id."""

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
    """Return prompt with prompt_id."""

    return Prompt.query.get(prompt_id)


def get_prompts_by_exercise(exercise_id):
    """Return prompts with exercise_id."""

    return Prompt.query.filter(Prompt.exercise_id == exercise_id).all()


def create_response(response_content, prompt, user, time_completed_exercise):
    """Create and return a new prompt."""

    response = ResponseToPrompt(response_content=response_content, 
                                prompt=prompt, 
                                user=user, 
                                time_completed_exercise=time_completed_exercise)

    return response


def get_responses():
    """Return all responses from database."""

    return ResponseToPrompt.query.all()    


def get_response_by_id(response_id):
    """Return response with response_id."""

    return ResponseToPrompt.query.get(response_id)


# Take in exercise_id, user_id.  Return that user's responses to prompts for that exercise.

# Should I print or get?
def print_exercise_responses_of_user(user_id, exercise_id):
    """Print all of user's responses for this exercise."""

    prompt_response_pairs = []

    responses = ResponseToPrompt.query.filter(ResponseToPrompt.user_id == user_id).join(Prompt).filter(Prompt.exercise_id == exercise_id).all() # returns list of responses
    # joinedload for eager loading?

    for response in responses:
        tup = (response.prompt.prompt_content, response.response_content)
        prompt_response_pairs.append(tup)

    for tup in prompt_response_pairs:
        # unpack the tuple
        (prompt_content, response_content) = tup
        print(f'Prompt: {prompt_content} Response: {response_content}')
    
    return prompt_response_pairs


def print_exercises_of_user(user_id):
    """Print all exercises user has responded to."""

    exercises = []

    responses = ResponseToPrompt.query.filter(ResponseToPrompt.user_id == user_id).join(Prompt).all() # list of responses of user

    # for response in responses:
    #     print("Exercise Title:", response.prompt.exercise.title, 
    #           "Prompt:", response.prompt.prompt_content, 
    #           "Response:", response.response_content)

    for response in responses:
        print("Exercise Title:", response.prompt.exercise.title)
        exercises.append(response.prompt.exercise)
    
    return exercises # a list of exercises


def get_exercises_of_user(user_id):
    """Get all exercises user has responded to."""

    exercises = []

    responses = ResponseToPrompt.query.filter(ResponseToPrompt.user_id == user_id).join(Prompt).all() # list of responses of user

    # for response in responses:
    #     print("Exercise Title:", response.prompt.exercise.title, 
    #           "Prompt:", response.prompt.prompt_content, 
    #           "Response:", response.response_content)

    for response in responses:
        # print("Exercise Title:", response.prompt.exercise.title)
        exercises.append(response.prompt.exercise)
    
    return exercises # a list of exercises


# # Take in exercise, print prompts
# def print_exercise_prompts(exercise):
#     # this_exercise = Exercise.query.filter(exercise.exercise_id == Exercise.exercise_id).one() # Alternative to .one() is .all() and then pull out only element of that list
#     for prompt in exercise.prompts:
#         print(prompt.responses) # Prints a list of responses per prompt.

# Exercise.query.filter(1 == Exercise.exercise_id).join(Prompt).all()

# Exercise.query.filter(1 == Exercise.exercise_id).options(db.joinedload('prompts')).one()



# def print_user_prompts(user):
#     print(ResponseToPrompt.query.filter(ResponseToPrompt.user == user).all())



# def print_exercise_responses(user, exercise):
#     """Print all of user's responses for this exercise."""

#     print(ResponseToPrompt.query.filter(ResponseToPrompt.user == user).join(Prompt).all())
#     filter for user
#     join prompt 
#     filter for exercise 

#     as a list

#     for response in user.responses:
#         if response.prompt.exercise == exercise:
#             print(response)

#     # user.responses filter by response.prompt.exercise = exercise
    
#     # print(user.responses)
#     print(User.query.filter(User.user_id == user.user_id))

#     # first_response = ResponseToPrompt.query.first(ResponseToPrompt.user_id == user.user_id) # Use the `user` input to get to the first (any) response of that user
#     # first_response.prompt.exercise
#     #     print(response)
#     #     for user_exercise in response.prompt.exercise: 
#     #         if user_exercise == exercise:
#     #             for element in exercise.prompts:

#     #             print(exercise.prompts.
#     #     for prompt in response.prompt:
#     #     print(prompt)
#     #     exercise = prompt.exercise
#     #     print(exercise)
#     #     if exercise not in exercises_of_user:
#     #         exercises_of_user.append(exercise)


# # Look at a user who has at least one response.
# # test_user = User.query.filter(len(User.responses) > 0).first()
# # print(test_user)

# # exercises_of_user = [] # Elements of list are unique exercises the user has done.

# # # for response in test_user.responses:
# # for response in User.query.first().responses:
# #     for prompt in response.prompt:
# #         print(prompt)
# #         exercise = prompt.exercise
# #         print(exercise)
# #         if exercise not in exercises_of_user:
# #             exercises_of_user.append(exercise)

# # print_exercise_responses(User.query.first(), choice(exercises_of_user))


def create_push_subscription(subscription_json, user):
    """Create a subscription to push notifications."""

    subscription = PushSubscription(subscription_json=subscription_json,
                                    user=user)

    return subscription


def get_first_subscription(subscription_json):
    """Get first subscription to push notifications."""

    first_subscription = PushSubscription.query.filter(PushSubscription.subscription_json == subscription_json).first()

    return first_subscription


def get_subscription_by_id(subscription_id):
    """Return subscription with subscription_id."""

    return PushSubscription.query.get(subscription_id)


# def get_subscription_json_by_id(subscription_id):
#     """Return subscription_json for subscription_id."""

#     return PushSubscription.query.get(subscription_id).subscription_json


def get_notifications():
    """Return notifications to deliver."""

    pacific_time = pytz.timezone("America/Los_Angeles")
    now = datetime.now(pacific_time)
    print(now)

    print(Notification.query.filter((now - Notification.last_sent) > timedelta(days=Notification.exercise.frequency)).all())

    return Notification.query.filter((now - Notification.last_sent) > timedelta(days=Notification.exercise.frequency)).all()

    # Handle first notif - OR last_sent None? 
    
    # 11:59 pm Day 0   11/27
    # Day 1   date   12:00   11/28

    # default last_sent at creation of notification

    


def get_users_notify():
    """Return users to be notified."""




def get_users_for_push():
    """Return users who should get push notifications."""

    pacific_time = pytz.timezone("America/Los_Angeles")
    now = datetime.now(pacific_time)
    print(now)

    # A dictionary where keys are users and each value is a set of exercises 
    # about which that user should be notified.  Put exercises in set because 
    # in one scheduled push, we want each user to get one notification per 
    # exercise.
    users_exercises_push = {}

    # There could be efficiency improvements in going through all notifs
    for notification in Notification.query.all():
        print(notification.user)
        print(notification.exercise)

        # gap is a timedelta object
        gap = now - notification.last_sent
        print(gap)
        print(notification.exercise.frequency)
        print(timedelta(days=notification.exercise.frequency))

        if gap > timedelta(days=notification.exercise.frequency):
            users_exercises_push[notification.user] = users_exercises_push.get(notification.user, {"exercises": set()})["exercises"].add(notification.exercise)
            # Can an object, can an instance of a class be a dictionary key?  Immutable?

        # Data structures are fun.  Am I making Python do too much?  
        # Use Object-Relational Mapping! 

    print(users_exercises_push)

    return users_exercises_push


def update_subscription_data_on_users_for_push():
    """Return users who get notifications, with respective subscription data."""

    pass


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