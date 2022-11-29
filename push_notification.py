"""Functions to send push notifications to users."""

import json
import os
from pywebpush import webpush, WebPushException
import pytz
from datetime import datetime
import crud
from model import connect_to_db, db

push_API_public_key = os.environ['VAPID_PUBLIC_KEY']
push_API_private_key = os.environ['VAPID_PRIVATE_KEY']
push_API_subject = os.environ['VAPID_CLAIM_EMAIL']


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


def send_push_for_test():
    """Push next notification of each notification whose time is due, for testing purposes."""

    # A current timestamp at the start of each time that this function runs, 
    # which is more organized than creating different timestamps throughout
    # various parts of the code within this function.  In one run of this job, 
    # all notifications evaluated within the job are evaluated against the 
    # same timestamp. 
    pacific_time = pytz.timezone("America/Los_Angeles")
    current = datetime.now(pacific_time)
    print(current)

    notifications_to_send = crud.get_notifications_to_send_for_test(current)
    print(notifications_to_send)

    for notification in notifications_to_send:
        user = notification.user
        exercise = notification.exercise
        print("\n\n\n\n", "LOOK HERE", notification, user, exercise)

        subscriptions = crud.get_subscriptions_from_notification(notification)
        print(subscriptions)
        for subscription in subscriptions:
            result = "OK"
            print(f"\n\n\n\n{result}")

            try:
                webpush(
                    subscription_info = json.loads(subscription.subscription_json), 
                    data = json.dumps({"title": f"*\O/* Ahoy, {user.first_name}",
                                       "body": f"Time to do {exercise.title} CURRENT: {current}"}),
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
        
        notification.last_sent = current
        db.session.commit()

    print("Job succeeded")

    # return


def send_push():
    """Push next notification of each notification whose time is due."""

    # A current timestamp at the start of each time that this function runs, 
    # which is more organized than creating different timestamps throughout
    # various parts of the code within this function.  In one run of this job, 
    # all notifications evaluated within the job are evaluated against the 
    # same timestamp. 
    pacific_time = pytz.timezone("America/Los_Angeles")
    current = datetime.now(pacific_time)
    print(current)

    notifications_to_send = crud.get_notifications_to_send(current)
    print(notifications_to_send)

    for notification in notifications_to_send:
        user = notification.user
        exercise = notification.exercise
        print(notification, user, exercise)

        subscriptions = crud.get_subscriptions_from_notification(notification)
        print(subscriptions)
        for subscription in subscriptions:
            result = "OK"
            print(f"\n\n\n\n{result}")

            try:
                webpush(
                    subscription_info = json.loads(subscription.subscription_json), 
                    data = json.dumps({"title": f"*\O/* Ahoy, {user.first_name}",
                                       "body": f"Time to do {exercise.title}"}),
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
        
        notification.last_sent = current
        db.session.commit()

    print("Job succeeded")
