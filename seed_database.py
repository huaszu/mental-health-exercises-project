"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime
import pytz

from flask_sqlalchemy import SQLAlchemy # Can I add these here?
from model import User, Exercise, Prompt

import crud
import model
import server

os.system("dropdb mental-health-platform")
os.system("createdb mental-health-platform")

model.connect_to_db(server.app)
model.db.create_all()


# user_role_opt_in = [True, False]

# Create test users.

for n in range(10):
    email = f"user{n}@test.com"  # Voila! A unique email!
    password = "test"
    first_name = f"Fname{n}"
    last_name = f"Lname{n}"
    pen_name = f"Mysterious{n}"
    # Seed some users who are only Experts, some who are only Consumers, and some who are both.
    if n in range(0, 4): # Users 0, 1, 2, 3
        is_expert = True
        is_consumer = False
    elif n in range(4, 7): # Users 4, 5, 6
        is_expert = False
        is_consumer = True
    else: # Users 7, 8, 9
        is_expert = True
        is_consumer = True

    user = crud.create_user(email=email, 
                            password=password, 
                            first_name=first_name,
                            last_name=last_name,
                            is_expert=is_expert,
                            is_consumer=is_consumer,
                            pen_name=pen_name)
    model.db.session.add(user)
    model.db.session.commit()


# Create test exercises, authored by test users who are experts.  

# Have one expert who has not authored any exercise.  Implies that user sets
# their ability to be an expert at the outset, instead of automatically
# turning on is_expert == True when a user creates an exercise ?!

exercise_frequencies = [1, 7, 14, 30]
time_limits = [None, 10, 20, 30]
expert_count = len(User.query.filter(User.is_expert == True).all())
experts_having_exercise_count = expert_count - 1
# print("EXPERTS HAVING EXERCISE:", experts_having_exercise) # 6
# Idea: Could distinguish between expert and author, i.e., if a user has 
# created an exercise, user could become author as well.

experts_having_exercise = User.query.filter(User.is_expert == True).limit(experts_having_exercise_count).all()

# Note: Each expert who has an exercise has exactly one exercise for now:
for user in experts_having_exercise:
# Beware of namespace and scoping.  Note that we have imported crud and model.  Can we use `user` here?
    title = f"Title{experts_having_exercise.index(user)}"
    description = "Description"
    frequency = choice(exercise_frequencies)
    time_limit_per_sitting = choice(time_limits)
    author = user
    # print("author:", author)

    exercise = crud.create_exercise(title=title, 
                                    description=description, 
                                    frequency=frequency, 
                                    time_limit_per_sitting=time_limit_per_sitting,
                                    author=author)
    model.db.session.add(exercise)
    model.db.session.commit()


# Create test prompts, within test exercises.

prompt_types = ["short answer", 
                "long answer", 
                "multiple choice - choose one", 
                "multiple choice - choose multiple"]

# Let's give 2 prompts to every exercise.
for exercise in Exercise.query.all():
    prompt_content1 = "Prompt"
    prompt_type1 = choice(prompt_types)
    exercise = exercise

    prompt1 = crud.create_prompt(prompt_content=prompt_content1, 
                                prompt_type=prompt_type1, 
                                exercise=exercise)

    prompt_content2 = "Prompt"
    prompt_type2 = choice(prompt_types)
    exercise = exercise

    prompt2 = crud.create_prompt(prompt_content=prompt_content2, 
                                prompt_type=prompt_type2, 
                                exercise=exercise)
    
    model.db.session.add_all([prompt1, prompt2])
    model.db.session.commit()


# Create 2 test responses for each prompt of each exercise. 

respondents = User.query.filter(User.is_consumer == True).all()

for exercise in Exercise.query.all():
    pacific_time = pytz.timezone("America/Los_Angeles")
    time_completed_exercise = datetime.now(pacific_time)

    for prompt in exercise.prompts:
        # print("prompt:", prompt)
        # response_content1 = "Response"
        response_content = "Response"
        # prompt1 = prompt
        user1 = choice(respondents)

        response1 = crud.create_response(response_content=response_content, 
                                         prompt=prompt, 
                                         user=user1,
                                         time_completed_exercise=time_completed_exercise)

        user2 = choice(respondents) # It is possible for the same user to have multiple responses to the same prompt, from doing that exercise on different occasions.

        response2 = crud.create_response(response_content=response_content, 
                                         prompt=prompt, 
                                         user=user2,
                                         time_completed_exercise=time_completed_exercise)


    model.db.session.add_all([response1, response2])
    model.db.session.commit()

#Print out all of that user's prompts and responses
# Show surveys user has responded to - viewing responses
# Making responses
# Creating forms