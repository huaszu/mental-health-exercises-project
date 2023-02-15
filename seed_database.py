"""Script to seed database."""

import os
from random import choice
from datetime import datetime
import pytz
from data.exercises import seed_experts, seed_exercise_details

from flask_sqlalchemy import SQLAlchemy
from model import User, Exercise, Prompt

import crud
import model
import server
import werkzeug.security

# Remove the existing database called "health"
os.system("dropdb health")

# Create an empty database called "health"
os.system("createdb health")

model.connect_to_db(server.app)
model.db.create_all()


# Create test users

for n in range(10):
    email = f"user{n}@test.com" # Voila! A unique email!
    password = "test"
    first_name = f"Fname{n}"
    last_name = f"Lname{n}"
    pen_name = f"Mysterious{n}"
    # Seed some users who are only Experts, some who are only Consumers, and some who are both
    if n in range(0, 4): # Users 0, 1, 2, 3
        is_expert = True
        is_consumer = False
    elif n in range(4, 7): # Users 4, 5, 6
        is_expert = False
        is_consumer = True
    else: # Users 7, 8, 9
        is_expert = True
        is_consumer = True
    
    # Hash password for security
    hashpw = werkzeug.security.generate_password_hash(password)

    # Create user
    user = crud.create_user(email=email, 
                            password=hashpw, 
                            first_name=first_name,
                            last_name=last_name,
                            is_expert=is_expert,
                            is_consumer=is_consumer,
                            pen_name=pen_name)

    # Add new record.  `db.session` stores planned modifications to database                        
    model.db.session.add(user)

# Commit transaction
model.db.session.commit()


# Prepare list of respondents who make test responses to exercises
respondents = User.query.filter(User.is_consumer == True).all()

# Create renowned expert users and author their exercises.

# Prompts can have four intended ways to respond
prompt_types = ["short answer", 
                "long answer", 
                "multiple choice - choose one", 
                "multiple choice - choose multiple"]

# `val` is a dictionary with key "exercises" and value being a dictionary
for name, val in seed_experts.items():
    split_name = name.split()
    # e.g., Brené Brown's `email_local_part` == BrenéBrown
    email_local_part = "".join(split_name)
    email = email_local_part + "@test.com"
    password = "test"
    first_name = split_name[0]
    last_name = split_name[1]
    pen_name = name
    is_expert = True
    is_consumer = True

    # Hash password for security
    hashpw = werkzeug.security.generate_password_hash(password)

    # Create user who is an expert
    user = crud.create_user(email=email, 
                            password=hashpw, 
                            first_name=first_name,
                            last_name=last_name,
                            is_expert=is_expert,
                            is_consumer=is_consumer,
                            pen_name=pen_name)
    model.db.session.add(user)

    # Create exercises, authored by this user 

    # `val["exercises"]` is a list of exercise titles
    for exercise_title in val["exercises"]:
        title = exercise_title
        # `seed_exercise_details[exercise_title]` is a dictionary containing 
        # keys of "description", "frequency", "time_limit_per_sitting", 
        # and "prompts"
        description = seed_exercise_details[exercise_title]["description"] 
        frequency = int(seed_exercise_details[exercise_title]["frequency"])
        time_limit_per_sitting = int(seed_exercise_details[exercise_title]["time_limit_per_sitting"])
        author = User.query.filter(User.pen_name == name).first()

        exercise = crud.create_exercise(title=title, 
                                        description=description, 
                                        frequency=frequency, 
                                        time_limit_per_sitting=time_limit_per_sitting,
                                        author=author)

        model.db.session.add(exercise)

        # Create prompts for every seed exercise

        prompt_type = "long answer"

        # `seed_exercise_details[exercise.title]` is a dictionary containing 
        # keys of "description", "frequency", "time_limit_per_sitting", 
        # and "prompts".
        # `seed_exercise_details[exercise.title]["prompts"]` is a list of 
        # strings that are prompts.
        for prompt_str in seed_exercise_details[exercise.title]["prompts"]:
            prompt_content = prompt_str

            prompt = crud.create_prompt(prompt_content=prompt_content, 
                                        prompt_type=prompt_type, 
                                        exercise=exercise)
            
            model.db.session.add(prompt)

            # Create 2 test responses for each prompt of each exercise 

            pacific_time = pytz.timezone("America/Los_Angeles")
            time_completed_exercise = datetime.now(pacific_time)

            response_content = "Response"

            # Randomly choose a respondent
            user1 = choice(respondents)
            response1 = crud.create_response(response_content=response_content, 
                                             prompt=prompt, 
                                             user=user1,
                                             time_completed_exercise=time_completed_exercise)
            
            # Allow for the same user to have multiple responses to the same 
            # prompt because a user can do an exercise on multiple occasions 
            user2 = choice(respondents) 
            response2 = crud.create_response(response_content=response_content, 
                                             prompt=prompt, 
                                             user=user2,
                                             time_completed_exercise=time_completed_exercise)

            model.db.session.add_all([response1, response2])

            # In this way of seeding responses for each prompt, it is possible 
            # for a user to respond to a subset of and not all prompts within 
            # an exercise.  A user randomly selected for one prompt may not 
            # get selected again for the next prompt of the same exercise, 
            # which aligns with how the app allows users to make 
            # submissions in which not all prompts have a response and which
            # aligns with reality of how users want to use the app, based on
            # user research.

# Committing a transaction takes a relatively long time so better to commit 
# once outside loop 
model.db.session.commit()
