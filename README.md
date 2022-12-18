# <The Hall of Mirrors>

## Description

The Hall of Mirrors is a web app for people to do journaling exercises that help them build emotional literacy, as well as for people to contribute exercises in service of this goal.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features for Users](#features-for-users)
- [Installation](#installation)
- [Tests](#tests)

## Tech Stack

- Python
- JavaScript
- HTML
- CSS
- Flask
- SQLAlchemy
- PostgreSQL
- Jinja2
- JSON
- Push API
- Service Worker API
- Notification API
- pywebpush library for Webpush Data encryption
- Python APScheduler library

## Features for Users

- Create account
- Log in
- View all exercises that can be done
- View exercises user has completed and corresponding prompts and responses
- Complete an exercise
- Create an exercise
- Get push notifications when it is time to do an exercise again

## Installation

#### Requirements:

- PostgreSQL
- Python 3.10
- VAPID public key, private key, and claim

To have this app running on your local computer, please follow the below steps:

Install PostgreSQL

Clone or fork this repository:
```
$ git clone https://github.com/huaszu/mental-health-exercises-project.git
```

Set up your own VAPID public key, private key, and claim to implement push notifications - https://blog.mozilla.org/services/2016/08/23/sending-vapid-identified-webpush-notifications-via-mozillas-push-service/.  Save them to secrets.sh.

Create a virtual environment inside your mental-health-exercises-project directory:
```
$ virtualenv env
```

Activate the virtual environment:
```
$ source env/bin/activate
```

Source from secrets.sh to your environment:
```
$ source secrets.sh
```

Install dependencies:
```
$ pip3 install -r requirements.txt
```

Create database 'health'.
```
$ createdb health
```
Create your database tables and seed example data.
```
$ python3 model.py
$ python3 seed_database.py
```
Run the app from the command line.
```
$ python3 server.py
```
If you want to use SQLAlchemy to query the database, run in interactive mode
```
$ python3 -i model.py
```

You can now navigate to 'localhost:5000/' to access the Hall of Mirrors.


    ```

## Tests

Examples on how to run them here.