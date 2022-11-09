# Next: Allow user to do an exercise from all exercises - tweaking logged out user experience
# Then: Author create exercise | Notification API
# Password hashing

# Delay React-ify all_exercises
# Later: At point of user complete exercise, capture date - order how to present exercises to user by date

"""Server for mental health exercises app."""

from flask import (Flask, render_template, request, flash, session, redirect, jsonify)
from model import connect_to_db, db
import crud
import requests

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """View homepage."""

    return render_template("homepage.html")

@app.route("/exercises")
def all_exercises():
    """View all exercises."""

    exercises = crud.get_exercises()

    return render_template("all_exercises.html", exercises=exercises)

@app.route("/add_exercise", methods=["POST"])
def add_to_all_exercises():
    """Create exercise and add it to db."""

    title = request.form.get("title")
    description = request.form.get("description")
    frequency = int(request.form.get("freq")) # Test that I get value # What if blank?
    time_limit_per_sitting = int(request.form.get("time-limit")) # What if blank? 

    user_id = session["user_id"]
    author = crud.get_user_by_id(user_id)

    exercise = crud.create_exercise(title=title, 
                                    description=description, 
                                    frequency=frequency, 
                                    time_limit_per_sitting=time_limit_per_sitting, 
                                    author=author)

    db.session.add(exercise)

    # Create the prompts, too?!

    db.session.commit()

    return redirect("/exercises")

@app.route("/users", methods=["POST"])
def register_user():
    """Create a new user."""

    email = request.form.get("email")
    password = request.form.get("password")
    first_name = request.form.get("first-name")
    last_name = request.form.get("last-name")
    pen_name = request.form.get("pen-name") # Later set default if left empty

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
        # Log in user by storing the user's email in session
        session["user_id"] = user.user_id
        flash(f"Welcome back, {user.first_name}!") # Funny - when user logs in with email in db and wrong password, get both the Welcome back and the incorrect flash messages
        # return redirect(f"/users/{user_id}") # If log in correctly, can redirect to user page? redirect(f"/users/{user_id}")
        return redirect("/users/my_exercises")

@app.route("/users/my_exercises")
def show_user_exercises():
    """Show exercises user has responded to."""

    user_id = session["user_id"]

    user = crud.get_user_by_id(user_id)
    exercises = crud.get_exercises_of_user(user_id) # This is a list

    # for exercise in exercises:
    #     prompts = crud.get_prompts_by_exercise(exercise.exercise_id) # This is a list

    return render_template("my_exercises.html", user=user, exercises=exercises)

@app.route("/exercises/<exercise_id>")
def show_exercise(exercise_id):
    """Show details on a particular exercise."""

    exercise = crud.get_exercise_by_id(exercise_id)

    # show_alert = True
    # if "user_id" in session:
    #     show_alert = False 
    # Does not work because program had already set show_alert and sent that data to the browser.  Not going to update show_alert once sent

    # I don't think I need session.modified = True because session["user_id"] is
    # what would change if user logs in on another tab.  We use 
    # session.modified = True when we change a value in an inner dictionary (?)

    return render_template("exercise_details.html", exercise=exercise, session=session)

@app.route("/exercises/<exercise_id>/submitted", methods=["POST"])
def save_user_responses(exercise_id):
    """Create a new set of saved responses for the user for the exercise."""
    
    # prompts = crud.get_prompts_by_exercise(exercise_id)
    # Note for later: time = datetime.now

    # Is there a way to write this function without the if, if we set it up
    # so that a user would only get routed here if the user is logged in
    # already?  Tangled with what my AJAX problem wants to solve

    print("\n\n\n\nWhat is request.json?", request.json)

    # destructure dictionary

    # print(request.json.get(""))
    # print and see what dict looks like

    # if "user_id" in session:
        # Save data to user
    user_id = session["user_id"]

    user = crud.get_user_by_id(user_id)
    # exercise = crud.get_exercise_by_id(exercise_id)

    for key in request.json:
        # print(key, request.form.get(key))
        response = crud.create_response(response_content=request.json.get(key), 
                                        prompt=crud.get_prompt_by_id(int(key)), 
                                        user=user)
        db.session.add(response)
    
    db.session.commit()

    return redirect("/users/my_exercises") 
    
@app.route("/login-status.json")
def get_login_status():
    """Get whether or not user is logged in."""

    print("user_id:", session.get("user_id"))

    if "user_id" in session:
        return jsonify(True)

    return jsonify(False)

# logout route
#     session.clear
#     return redirect to '/'


@app.route("/create")
def create():
    """Create an exercise."""

    return render_template("create.html") # Can only get here if logged in
    # Can let someone give themselves a pen name at this point!


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)