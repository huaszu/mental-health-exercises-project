"""Functions to send push notifications to users."""

import json
import os
from pywebpush import webpush, WebPushException
import pytz
from datetime import datetime
import crud
from model import db
from constants import PACIFIC_TIMEZONE_CITY

push_API_public_key = os.environ['VAPID_PUBLIC_KEY']
push_API_private_key = os.environ['VAPID_PRIVATE_KEY']
push_API_subject = os.environ['VAPID_CLAIM_EMAIL']


def send_first_push(subscription):
    """Push a notification.  Takes in a PushSubscription object."""

    result = "OK"

    try:
        # Encode `data`, add appropriate VAPID auth headers, and send
        # to the push server identified in `subscription_info`
        webpush(
            subscription_info = json.loads(subscription.subscription_json), 
            data = json.dumps({"title": "*\O/* Ahoy",
                               "body": "A notification will look like this one."}),
            vapid_private_key = push_API_private_key, 
            vapid_claims = {"sub": push_API_subject}
        )
    # Handle exception
    except WebPushException as ex:
        print(ex, repr(ex))
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message)
        result = "FAILED"

    return result


def send_push():
    """Push next notification of each notification whose time is due."""

    # Store current timestamp in Pacific Time.  Using a current timestamp at 
    # the start of each time that this function runs is more organized than 
    # creating different timestamps throughout various parts of the code 
    # within this function.  In one run of this job, evaluate all 
    # notifications within the job against the same timestamp. 
    pacific_time = pytz.timezone(PACIFIC_TIMEZONE_CITY)
    current = datetime.now(pacific_time)

    # Get notifications whose time is due to be sent again.
    notifications_to_send = crud.get_notifications_to_send(current)

    for notification in notifications_to_send:
        # Identify the user and the exercise of this notification
        user = notification.user
        exercise = notification.exercise

        # Get subscription(s) corresponding to this notification
        subscriptions = crud.get_subscriptions_from_notification(notification)

        for subscription in subscriptions:
            result = "OK"

            try:
                # Encode `data`, add appropriate VAPID auth headers, and send
                # to the push server identified in `subscription_info`
                webpush(
                    subscription_info = json.loads(subscription.subscription_json), 
                    data = json.dumps({"title": f"*\O/* Ahoy, {user.first_name}",
                                       "body": f"Time to do {exercise.title}"}),
                    vapid_private_key = push_API_private_key, 
                    vapid_claims = {"sub": push_API_subject}
                )
            # Handle exception
            except WebPushException as ex:
                print(ex, repr(ex))
                if ex.response and ex.response.json():
                    extra = ex.response.json()
                    print("Remote service replied with a {}:{}, {}",
                        extra.code,
                        extra.errno,
                        extra.message)
                result = "FAILED"
        
        # Update information on when this notification was last sent, which
        # is used to compute which notifications are due to be sent again
        notification.last_sent = current

        db.session.commit()

    print("Job succeeded")


# TODO: Write helper function to make the try/except block in the
# `send_first_push(subscription)` and `send_push()` functions more DRY.
    # `subscription_info`, `vapid_private_key`, and `vapid_claims` behave
    # similarly in both functions.
    # `data` differs in the two functions because the text to show users in 
    # the very first notification is the same warm welcome, as shown in 
    # `send_first_push(subscription)`, while the text to show users in
    # subsequent notifications focuses on encouraging a user to revisit a 
    # specific exercise.  The latter therefore tailors the notification text
    # to mention the pertinent exercise title, in addition to having the 
    # personalization of mentioning the user's name