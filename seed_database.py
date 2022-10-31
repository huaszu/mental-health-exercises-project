"""Script to seed database."""

import os
import json
from random import choice, randint
from datetime import datetime

import crud
import model
import server

os.system("dropdb mental-health-platform")
os.system('createdb mental-health-platform')

model.connect_to_db(server.app)
model.db.create_all()


# user_role_opt_in = [True, False]

for n in range(10):
    email = f'user{n}@test.com'  # Voila! A unique email!
    password = 'test'
    first_name = f'Fname{n}'
    last_name = f'Lname{n}'
    pen_name = f'Mysterious{n}'
    # Seed some users who are only Experts, some who are only Consumers, and some who are both.
    if n in range(0, 4): # Users 0, 1, 2, 3
        is_expert = True
        is_consumer = False
    elif n in range(4, 7): # Users 4, 5, 6
        is_expert = False
        is_consumer = True
    else: # Users 7, 8, 9, 10
        is_expert = True
        is_consumer = True

    user = crud.create_user(email=email, 
                            password=password, 
                            first_name=first_name,
                            last_name=last_name,
                            pen_name=pen_name,
                            is_expert=is_expert,
                            is_consumer=is_consumer)
    model.db.session.add(user)
    model.db.session.commit()