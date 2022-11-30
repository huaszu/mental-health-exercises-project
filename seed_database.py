"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime
import pytz
import re
from data.exercises import seed_experts, seed_exercise_details

from flask_sqlalchemy import SQLAlchemy # Can I add these here?
from model import User, Exercise, Prompt

import crud
import model
import server

os.system("dropdb health")
os.system("createdb health")

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

# Create renowned experts and author their exercises.

prompt_types = ["short answer", 
        "long answer", 
        "multiple choice - choose one", 
        "multiple choice - choose multiple"]

for name, val in seed_experts.items(): # val is a dict with key "exercises" and value being a dict
    # Create renowned experts.

    # .split() splits on whitespace by default
    split_name = name.split()
    email_local_part = "".join(split_name) # e.g., Brené Brown's email_local_part is BrenéBrown
    email = email_local_part + "@test.com"
    password = "test"
    first_name = split_name[0]
    last_name = split_name[1]
    pen_name = name
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

    # Seed exercises, authored by users who are renowned experts. 

    for exercise_title in val["exercises"]: # val["exercises"] is a list of exercise titles
        title = exercise_title
        description = seed_exercise_details[exercise_title]["description"] # seed_exercise_details[exercise_title] is a dict containing keys of "description", "frequency", "time_limit_per_sitting", and "prompts"
        frequency = int(seed_exercise_details[exercise_title]["frequency"])
        time_limit_per_sitting = int(seed_exercise_details[exercise_title]["time_limit_per_sitting"])
        author = User.query.filter(User.pen_name == name).first()

        exercise = crud.create_exercise(title=title, 
                                        description=description, 
                                        frequency=frequency, 
                                        time_limit_per_sitting=time_limit_per_sitting,
                                        author=author)
        # Alternative: Add exercise to list and loop over that list.  Do not do `for exercise in Exercise.query.all()` later

        model.db.session.add(exercise)

        # Create prompts for every seed exercise.

        prompt_type = "long answer"

        # seed_exercise_details[exercise.title] is a dict containing keys of "description", "frequency", "time_limit_per_sitting", and "prompts"
        for prompt_str in seed_exercise_details[exercise.title]["prompts"]: # seed_exercise_details[exercise.title]["prompts"] is a list of strings that are prompts
            prompt_content = prompt_str

            prompt = crud.create_prompt(prompt_content=prompt_content, 
                                        prompt_type=prompt_type, 
                                        exercise=exercise)
            
            model.db.session.add(prompt)

model.db.session.commit()
# Commit takes a long time so better to commit once outside loop 

# Can make helper fn inside loop if code unwieldy



# # Create 2 test responses for each prompt of each exercise. 

# respondents = User.query.filter(User.is_consumer == True).all()

# for exercise in Exercise.query.all():
#     pacific_time = pytz.timezone("America/Los_Angeles")
#     time_completed_exercise = datetime.now(pacific_time)

#     for prompt in exercise.prompts:
#         # print("prompt:", prompt)
#         # response_content1 = "Response"
#         response_content = "Response"
#         # prompt1 = prompt
#         user1 = choice(respondents)

#         response1 = crud.create_response(response_content=response_content, 
#                                          prompt=prompt, 
#                                          user=user1,
#                                          time_completed_exercise=time_completed_exercise)

#         user2 = choice(respondents) # It is possible for the same user to have multiple responses to the same prompt, from doing that exercise on different occasions.

#         response2 = crud.create_response(response_content=response_content, 
#                                          prompt=prompt, 
#                                          user=user2,
#                                          time_completed_exercise=time_completed_exercise)


#     model.db.session.add_all([response1, response2])
#     model.db.session.commit()

#Print out all of that user's prompts and responses
# Show surveys user has responded to - viewing responses
# Making responses
# Creating forms
