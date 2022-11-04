# Next: When user has logged in, show me what exercises, prompts, responses I have done
# Then: Allow user to do an exercise from all exercises

# Delay React-ify all exercises
# Later: At point of user complete exercise, capture date - order how to present exercises to user by date

"""Server for mental health exercises app."""

from flask import (Flask, render_template, request, flash, session, redirect)
from model import connect_to_db, db
import crud

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
        user = crud.create_user(email, password, first_name, last_name, is_expert, is_consumer, pen_name)
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

    return render_template("exercise_details.html", exercise=exercise)

@app.route("/exercises/<exercise_id>/submitted", methods=["POST"])
def get_user_to_save(exercise_id):

    if "user_id" in session:
        # Save data to user
    # Temporarily save data and alert user to sign in if want data saved
    

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)