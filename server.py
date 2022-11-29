"""Server for mental health exercises app."""

from flask import (Flask, render_template, request, flash, session, redirect, jsonify, make_response, send_from_directory)
from model import connect_to_db, db
import crud
from datetime import datetime
import pytz
from pywebpush import webpush, WebPushException
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests
import os

from jinja2 import StrictUndefined

app = Flask(__name__, instance_relative_config=True)

# Load configuration setup for use of MDN Push API
app.config.from_pyfile('application.cfg.py')

# MAKE SURE SESSION IS STILL WORKING!

app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

push_API_public_key = os.environ['VAPID_PUBLIC_KEY']
push_API_private_key = os.environ['VAPID_PRIVATE_KEY']
push_API_subject = os.environ['VAPID_CLAIM_EMAIL']


# This function can take in 1) a dictionary having users as keys and each 
# value is a set of exercises about which that user should be notified, 
# and 2) a dictionary having users as keys and each value is a set of 
# PushSubscription objects associated with that user.  We use 1) to customize 
# content in the notification and 2) to deliver the notification.
# Alternative: Take in one dictionary where each key is a user and the value 
# of each key is another dictionary, where one key is "exercises", with 
# value as set of exercises, and another key is "subscriptions", with value
# as set of subscriptions.  
# Expect that a user will usually be associated with one subscription.  An 
# edge case is that a user has multiple subscriptions, if the user has logged 
# in on multiple browsers. 
def push_on_schedule():
    """Create a push notification."""

    # Get subscriber
    # sub = json.loads(request.form["sub"])

    sub = crud.get_subscription_by_id(3).subscription_json
    # print(f"\n\n\n\n{sub}")
    # print(type(sub))

    # Will have to do json.loads(sub) because of error `  File "/Users/hsy/src/mental-health-exercises-project/server.py", line 341, in push
#     webpush(
#   File "/Users/hsy/src/mental-health-exercises-project/env/lib/python3.10/site-packages/pywebpush/__init__.py", line 447, in webpush
#     url = urlparse(subscription_info.get('endpoint'))
# AttributeError: 'str' object has no attribute 'get'`

    # Test push notification
    result = "OK"
    print(f"\n\n\n\n{result}")

    try:
        webpush(
            subscription_info = json.loads(sub), 
            data = json.dumps({"title": "*\O/* Ahoy",
                               "body": "A notification will look like this one."}),
            # data = json.dumps({"title": "Test /push route",
            #                    "body": "Yes, it works"}),
            vapid_private_key = push_API_private_key, 
            vapid_claims = {"sub": push_API_subject}
        )
    except WebPushException as ex:
        print(ex, repr(ex))
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message)
        result = "FAILED"

    # print(result)

    return result

    # To handle first notif: For users who have subscriptions, scheduled task can check for if (gap between now and time_completed exercise) > frequency
    # time_completed_exercise is on response - go through prompt to get to exercise
    # Does user have to have completed an exercise to get notifs?  If no - record subscription creation time and use that time to help make first notif
    # How about I edit so that complete an exercise -> redirect back to not filled out exercise page and then show enable push messaging button
    # Or at response creation - see below

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=push_on_schedule, trigger="interval", seconds=60)
# scheduler.start()

@app.route("/")
def show_homepage():
    """View homepage."""

    return render_template("homepage.html")

@app.route("/exercises")
def show_all_exercises():
    """View all exercises."""

    exercises = crud.get_exercises()

    # Decide whether to show newest added exercises at top or bottom, or elsewhere

    return render_template("all_exercises.html", 
                           exercises=exercises)

@app.route("/add_exercise", methods=["POST"])
def add_to_all_exercises():
    """Create exercise and add it to db."""

    # Create exercise
    title = request.form.get("title", None) # None interpreted as null
    # None as default value in case "title" is not present
    description = request.form.get("description")
    try:
        frequency = int(request.form.get("freq")) 
    except:
        frequency = None
    # Test that I get value # What if blank?
    try:
        time_limit_per_sitting = int(request.form.get("time-limit"))
    except:
        time_limit_per_sitting = None
    # What if blank? 
    # If blank, int() gives Traceback: 
    # `ValueError: invalid literal for int() with base 10: ''`

    user_id = session["user_id"]
    author = crud.get_user_by_id(user_id)

    exercise = crud.create_exercise(title=title, 
                                    description=description, 
                                    frequency=frequency, 
                                    time_limit_per_sitting=time_limit_per_sitting, 
                                    author=author)

    db.session.add(exercise)
    # db.session.commit()

    # Create prompt(s) within exercise
    for prompt_content in request.form.getlist("prompt"):
        
        # To add: If prompt_content is blank, do not create blank prompt

        prompt = crud.create_prompt(prompt_content=prompt_content, exercise=exercise)
        # Not giving a value for prompt_type and letting prompt_type default
        # to "long answer"

        db.session.add(prompt)

        # Right now if user clicks `Add prompt` button and then decides
        # not to provide any value for the additional prompt, we would be
        # adding a prompt to the db with blank prompt_content (to be checked)

    author.is_expert = True

    try:
        db.session.commit()
    except:
        flash("Be careful how you fill out the form!") # Don't know the circumstances in which this flash would show
        return redirect("/create")

    return redirect("/exercises")

@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""

    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("first-name")
    last_name = request.form.get("last-name")
    pen_name = request.form.get("pen-name") # Later set default if left empty

    # Data Integrity
    # Possible ways to handle pen_name include: 
    # in crud fn, OR
    # (when render, plug in a pen name, and
    # allow null in db - tracks that user did not want a pen name)

    is_expert = False
    is_consumer = True
    # pen_name = "pen"

    user = crud.get_user_by_email(email)
    if user:
        flash("Cannot create an account with that email. Try again.")
        # print("user is already a user") # This works, so `if user:` is evaluating as we expect
    else:
        user = crud.create_user(email=email, 
                                password=password, 
                                first_name=first_name, 
                                last_name=last_name, 
                                is_expert=is_expert, 
                                is_consumer=is_consumer, 
                                pen_name=pen_name)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")

    return redirect("/")

@app.route("/login", methods=["POST"])
def process_login():
    """Process user login."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)

    if user == None: # is this not repetitive with `elif not user` ?
        flash("We don't have an account for you under this email!")
        return redirect("/")
    elif not user or user.password != password:
        flash("The email or password you entered was incorrect.")
        return redirect("/")
    else:
        # Log in user by storing the user's id in session
        session["user_id"] = user.user_id
        flash(f"Welcome back, {user.first_name}!") # Funny - when user logs in 
        # with email in db and wrong password, get both the Welcome back and 
        # the incorrect flash messages.  No longer replicating this error.

        return redirect("/users/my_exercises")

@app.route("/users/my_exercises")
def show_user_exercises():
    """Show exercises user has responded to."""

    try:
        user_id = session["user_id"]

        user = crud.get_user_by_id(user_id)
        exercises = crud.get_exercises_of_user(user_id) # This is a list

        # for exercise in exercises:
        #     prompts = crud.get_prompts_by_exercise(exercise.exercise_id) # This is a list

        return render_template("my_exercises.html", user=user, exercises=exercises)
    
    # If user is not logged in, say if user comes here by typing 
    # "/users/my_exercises" in the URL bar instead of by being redirected here
    # from logging in.
    except:
        flash("Log in to see exercises you have completed.")
        return redirect("/")

@app.route("/exercises/<exercise_id>")
def show_exercise(exercise_id):
    """Show details on a particular exercise."""

    exercise = crud.get_exercise_by_id(exercise_id)

    day = "day"
    if exercise.frequency != 1:
        day = str(exercise.frequency) + " days"

    # I don't think I need session.modified = True because session["user_id"] is
    # what would change if user logs in on another tab.  We use 
    # session.modified = True when we change a value in an inner dictionary (?)

    return render_template("exercise_details.html", exercise=exercise, day=day)

@app.route("/exercises/<exercise_id>/submitted", methods=["POST"])
def save_user_responses(exercise_id):
    """Create a new group of saved responses for the user for the exercise."""
    
    # prompts = crud.get_prompts_by_exercise(exercise_id)

    # Is there a way to write this function without the if, if we set it up
    # so that a user would only get routed here if the user is logged in
    # already?  Tangled with what my AJAX problem wants to solve

    print("\n\n\n\nWhat is request.json?", request.json)

    # destructure dictionary

    # print(request.json.get(""))
    # print and see what dict looks like

    # if "user_id" in session:
        # Save data to user
    
    pacific_time = pytz.timezone("America/Los_Angeles")
    time_completed_exercise = datetime.now(pacific_time)
    # Associate one time with all responses from the same form, as opposed to
    # a different time with each response from the same form.
    
    user_id = session["user_id"]

    user = crud.get_user_by_id(user_id)
    # exercise = crud.get_exercise_by_id(exercise_id)

    for key in request.json:
        # print(key, request.form.get(key))
        response = crud.create_response(response_content=request.json.get(key), 
                                        prompt=crud.get_prompt_by_id(int(key)), 
                                        user=user,
                                        time_completed_exercise=time_completed_exercise)
        db.session.add(response)
    
    db.session.commit()

    # Check if user has subscription -> add a notif for future OR alternative
    # see above in scheduled task function
    # One scheduled task that seeds notifs and another scheduled task for sending them
    # first_send in notifs table <- if first_send today, then send today

    # Schedule task: You have a subscription, you completed exercise on this day, generate a future first notif
    # Another schedule task: send first notifs - only want the day - if today == the day

    return redirect("/users/my_exercises") 
    
@app.route("/login-status.json")
def get_login_status():
    """Get whether or not user is logged in."""

    print("user_id:", session.get("user_id"))

    if "user_id" in session:
        return jsonify(True)

    return jsonify(False)

@app.route("/logout")
def process_logout():
    """Process user logout."""

    session.clear()
    return redirect("/")

@app.route("/create")
def create():
    """Create an exercise."""
    
    # If user is not logged in, redirect user to log in.  Only logged in users
    # can create exercises. 
    if "user_id" not in session:
        flash("Please log in if you want to make an exercise.")
        return redirect("/") 
        # Haha alternative: Show user 403 Permission Forbidden error

    return render_template("create.html") # Can only get here if logged in
    # Can let someone give themselves a pen name at this point!  Fix blank pen names later

# Route currently not in use:
@app.route("/service_worker.js")
def allow_sw_scope_with_http_header():
    """Override path restriction that limits scope of sw script."""

    # Service Worker Script Response:
    # An HTTP response to a service worker's script resource request can 
    # include the following header:

    # `Service-Worker-Allowed`
    # Indicates the user agent will override the path restriction, which 
    # limits the maximum allowed scope url that the script can control, to 
    # the given value.

    # Note: The value is a URL. If a relative URL is given, it is parsed 
    # against the script’s URL.

    # In addition to the origin restriction, service workers are restricted by 
    # the path of the service worker script. For example, a service worker 
    # script at https://www.example.com/~bob/sw.js can be registered for the 
    # scope url https://www.example.com/~bob/ but not for the scope 
    # https://www.example.com/ or https://www.example.com/~alice/. This 
    # provides some protection for sites that host multiple-user content in 
    # separated directories on the same origin. However, the path restriction 
    # is not considered a hard security boundary, as only origins are. Sites 
    # are encouraged to use different origins to securely isolate segments of 
    # the site if appropriate.

    # Servers can remove the path restriction by setting a 
    # Service-Worker-Allowed header on the service worker script.
    # https://www.w3.org/TR/service-workers/

    response = make_response(send_from_directory(app.static_folder, "/js/service_worker.js"))
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Content-Type"] = "application/javascript"
    print(response)
    return response


@app.route("/vapid_public.json")
def get_vapid_public_key():
    """Get VAPID public key for Push API."""

    # print("VAPID Public Key:", push_API_public_key)

    return jsonify(push_API_public_key)


def send_first_push(subscription):
    """Push a notification.  Takes in a PushSubscription object."""

    result = "OK"
    print(f"\n\n\n\n{result}")

    try:
        webpush(
            subscription_info = json.loads(subscription.subscription_json), 
            data = json.dumps({"title": "*\O/* Ahoy",
                               "body": "A notification will look like this one."}),
            vapid_private_key = push_API_private_key, 
            vapid_claims = {"sub": push_API_subject}
        )
    except WebPushException as ex:
        print(ex, repr(ex))
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message)
        result = "FAILED"

    print("ending result:", result)

    return result


@app.route("/api/push-subscriptions", methods=["POST"])
def initiate_push():
    """Create a push subscription if necessary and spawn first notification."""

    # Is subscription unique for every user? 
    # Is subscription unique for every user for every time user permits push
    # notifications from not having permitted them?

    user_id = session["user_id"]
    user = crud.get_user_by_id(user_id)

    json_data = request.json # vs request.get_json() ?
    subscription_json = json_data["subscription_json"]
    print(subscription_json)

    exercise_id = json_data["exercise_id"]
    print("EXERCISE:", exercise_id)
    
    # Check if there is already a matching PushSubscription object with the same 
    # subscription_json because when we reload the page, even when the browser 
    # resends the same subscription_json due to invoking the 
    # registerServiceWorker function again, we will not cause an error on the 
    # server. 
    subscription = crud.get_first_subscription(subscription_json=subscription_json)

    # If there is no PushSubscription object with matching subscription_json, 
    # create a new PushSubscription object.
    if subscription is None:
        print("Let's create")
        subscription = crud.create_push_subscription(subscription_json=subscription_json, 
                                                     user=user)

        db.session.add(subscription)

    # Spawn first notification.
    send_first_push(subscription)

    # notification = crud.create_notification(user=user, exercise, last_sent)

    db.session.commit()

    return jsonify({
        "status": "success"
    })


# @app.route("/push", methods=["POST"])
# def push():
#     """Spawn a push notification."""

#     # Get subscriber
#     # sub = json.loads(request.form["sub"])

#     sub = crud.get_subscription_by_id(1).subscription_json # Hard-coded a specific subscription id that was known to exist for testing
#     # print(f"\n\n\n\n{sub}")
#     # print(type(sub))

#     # Will have to do json.loads(sub) because of error `  File "/Users/hsy/src/mental-health-exercises-project/server.py", line 341, in push
# #     webpush(
# #   File "/Users/hsy/src/mental-health-exercises-project/env/lib/python3.10/site-packages/pywebpush/__init__.py", line 447, in webpush
# #     url = urlparse(subscription_info.get('endpoint'))
# # AttributeError: 'str' object has no attribute 'get'`

#     # Test push notification
#     result = "OK"
#     print(f"\n\n\n\n{result}")

#     try:
#         webpush(
#             subscription_info = json.loads(sub), 
#             data = json.dumps({"title": "*\O/* Ahoy",
#                                "body": "A notification will look like this one."}),
#             # data = json.dumps({"title": "Test /push route",
#             #                    "body": "Yes, it works"}),
#             vapid_private_key = push_API_private_key, 
#             vapid_claims = {"sub": push_API_subject}
#         )
#     except WebPushException as ex:
#         print(ex, repr(ex))
#         if ex.response and ex.response.json():
#             extra = ex.response.json()
#             print("Remote service replied with a {}:{}, {}",
#                   extra.code,
#                   extra.errno,
#                   extra.message)
#         result = "FAILED"

#     # print(result)

#     return result


# Remember to send notifs through subscription to user(s), as in, for this subscription, 
# which of the associated users should get a notif today


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)